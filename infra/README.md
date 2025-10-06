# DocuChat Infrastructure

این پوشه شامل تمام فایل‌های Infrastructure as Code برای DocuChat است.

## ساختار

```text
infra/
├── docker-compose.yml          # محیط توسعه محلی
├── chart/                      # Helm chart برای Kubernetes
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment-backend.yaml
│       ├── deployment-frontend.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── cronjob-billing.yaml
│       ├── prometheus-deployment.yaml
│       ├── grafana-deployment.yaml
│       └── ...
├── prometheus/                 # تنظیمات Prometheus
│   ├── prometheus.yml
│   ├── prometheus-docker.yml   # برای docker-compose
│   └── alerts.yml
├── grafana/                    # تنظیمات Grafana
│   ├── datasources.yaml
│   └── dashboards/
│       ├── backend-overview.json
│       └── token-usage.json
├── runbook/                    # راهنماهای بازیابی
│   ├── recovery-db.md
│   ├── rotate-secrets.md
│   └── scale-gpu.md
└── terraform/                  # (اختیاری) Terraform برای cloud resources
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## راه‌اندازی سریع

### محیط محلی (Docker Compose)

```bash
# از root directory پروژه
cd infra/
docker-compose up -d

# بررسی وضعیت
docker-compose ps

# مشاهده لاگ‌ها
docker-compose logs -f
```

**سرویس‌های در دسترس:**

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3001> (admin/admin)

### Kubernetes (Production)

```bash
# Deploy با Helm
helm upgrade --install docuchat ./chart \
  --namespace docuchat-prod \
  --create-namespace \
  --set secrets.openaiApiKey=$OPENAI_API_KEY \
  --set secrets.databaseUrl=$DATABASE_URL \
  --set secrets.zibalApiKey=$ZIBAL_API_KEY

# بررسی وضعیت
kubectl get pods -n docuchat-prod

# مشاهده لاگ‌ها
kubectl logs -l app.kubernetes.io/component=backend -n docuchat-prod
```

## تنظیمات

### متغیرهای محیطی

یک فایل `.env` در root پروژه ایجاد کنید:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/docuchat

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET=your-secret-here

# Payment
ZIBAL_API_KEY=zibal-key-here

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin
```

### Helm Values

فایل `chart/values.yaml` را برای تنظیمات production ویرایش کنید:

```yaml
image:
  backend:
    repository: ghcr.io/your-org/docuchat-backend
    tag: latest
  frontend:
    repository: ghcr.io/your-org/docuchat-frontend
    tag: latest

ingress:
  enabled: true
  hosts:
    - host: docuchat.example.com
      paths:
        - path: /api
          service: backend
        - path: /
          service: frontend

resources:
  backend:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "2000m"
```

## Monitoring

### Prometheus

**Metrics endpoint:** <http://localhost:8000/api/v1/metrics>

**کلیدی‌ترین متریک‌ها:**

- `openai_tokens_total` - مصرف توکن OpenAI
- `ml_fallback_total` - تعداد fallback بین مدل‌ها
- `http_request_duration_seconds` - زمان پاسخ HTTP
- `rag_query_total` - کوئری‌های RAG

### Grafana Dashboards

1. **Backend Overview** - کلیات عملکرد backend
2. **Token Usage & Billing** - مصرف توکن و هزینه‌ها

**دسترسی:**

- محیط محلی: <http://localhost:3001>
- Production: <https://grafana.docuchat.example.com>

## Billing

سیستم صدور صورتحساب روزانه (CronJob):

```yaml
schedule: "0 3 * * *"  # هر روز ساعت 3 صبح
```

**عملکرد:**
1. کوئری Prometheus برای مصرف توکن
2. محاسبه هزینه (20 تومان / 1000 توکن)
3. ایجاد رکورد در جدول `tenant_invoice`
4. ایجاد لینک پرداخت زیبال
5. ارسال ایمیل به tenant

**اجرای دستی:**

```bash
kubectl create job --from=cronjob/docuchat-billing manual-billing -n docuchat-prod
kubectl logs job/manual-billing -n docuchat-prod
```

## Disaster Recovery

راهنماهای کامل در `runbook/`:

- **recovery-db.md** - بازیابی پایگاه داده
- **rotate-secrets.md** - چرخش کلیدهای امنیتی
- **scale-gpu.md** - مقیاس‌پذیری GPU

## CI/CD

Workflows در `.github/workflows/`:

- **ci.yml** - Build, test, و push images
- **deploy.yml** - Deploy به Kubernetes

**Trigger deployment:**

```bash
# ایجاد tag جدید
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# یا اجرای دستی
gh workflow run deploy.yml -f environment=production
```

## امنیت

### Secrets در Kubernetes

```bash
# ایجاد secret
kubectl create secret generic docuchat-secrets \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --namespace docuchat-prod

# یا از فایل
kubectl create secret generic docuchat-secrets \
  --from-env-file=.env.production \
  --namespace docuchat-prod
```

### Network Policy

فعال‌سازی Network Policy برای محدود کردن ترافیک:

```yaml
networkPolicy:
  enabled: true
  policyTypes:
    - Ingress
    - Egress
```

## مقیاس‌پذیری

### Horizontal Pod Autoscaler

```yaml
autoscaling:
  backend:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
```

### Manual Scaling

```bash
# افزایش تعداد replica
kubectl scale deployment/docuchat-backend --replicas=5 -n docuchat-prod

# یا با Helm
helm upgrade docuchat ./chart \
  --set replicaCount.backend=5
```

## Troubleshooting

### بررسی لاگ‌ها

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n docuchat-prod --tail=100

# مشاهده زنده
kubectl logs -f deployment/docuchat-backend -n docuchat-prod
```

### Debug Pod

```bash
# باز کردن shell در pod
kubectl exec -it deployment/docuchat-backend -n docuchat-prod -- /bin/bash

# بررسی متغیرهای محیطی
kubectl exec deployment/docuchat-backend -n docuchat-prod -- env | grep OPENAI
```

### Port Forwarding

```bash
# دسترسی محلی به backend
kubectl port-forward svc/docuchat-backend 8000:8000 -n docuchat-prod

# دسترسی به database
kubectl port-forward svc/postgresql 5432:5432 -n docuchat-prod
```

## پشتیبانی

برای راهنمای کامل، به [docs/fa/devops-guide.md](../docs/fa/devops-guide.md) مراجعه کنید.

**تماس:**
- DevOps Team: devops@docuchat.io
- On-call: oncall@docuchat.io

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.
