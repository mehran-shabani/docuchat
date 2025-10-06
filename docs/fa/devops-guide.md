# راهنمای DevOps - DocuChat

## فهرست مطالب

1. [معماری](#معماری)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [مانیتورینگ و Observability](#مانیتورینگ-و-observability)
4. [سیستم صدور صورتحساب](#سیستم-صدور-صورتحساب)
5. [امنیت و مدیریت Secrets](#امنیت-و-مدیریت-secrets)
6. [Disaster Recovery](#disaster-recovery)
7. [مقیاس‌پذیری](#مقیاسپذیری)
8. [محیط توسعه محلی](#محیط-توسعه-محلی)

---

## معماری

### اجزای سیستم

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │  Prometheus  │  │
│  │  (Next.js)   │  │  (FastAPI)   │  │              │  │
│  │  Replicas: 2 │  │  Replicas: 2 │  │  Retention:  │  │
│  │              │  │              │  │    30 days   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│  ┌──────▼─────────────────▼─────────────────▼───────┐  │
│  │              Ingress Controller                   │  │
│  │         (NGINX + Let's Encrypt SSL)               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │   Grafana    │ │
│  │  (pgvector)  │  │   (Cache)    │  │ (Dashboard)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │        Billing CronJob (Daily at 3 AM)          │   │
│  │  - Query Prometheus metrics                      │   │
│  │  - Calculate token costs                         │   │
│  │  - Generate invoices                             │   │
│  │  - Send payment links via Zibal                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### متغیرهای محیطی مورد نیاز

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/docuchat

# Cache
REDIS_URL=redis://host:6379/0

# Authentication
JWT_SECRET=your-secret-key-here

# Payment Gateway
ZIBAL_API_KEY=zibal-...

# Monitoring
GRAFANA_ADMIN_PASSWORD=strong-password

# Kubernetes
K8S_NAMESPACE=docuchat-prod
KUBECONFIG_B64=base64-encoded-kubeconfig

# Container Registry
GHCR_USERNAME=your-github-username
GHCR_TOKEN=ghp_...
```

---

## CI/CD Pipeline

### معماری CI/CD

```
┌──────────────┐
│  Git Push    │
│  (main/tags) │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│        GitHub Actions - CI               │
├─────────────────────────────────────────┤
│  1. Checkout code                        │
│  2. Setup Python 3.11 & Node 20          │
│  3. Install dependencies                 │
│  4. Run linters (ruff, tsc)              │
│  5. Run tests (pytest, vitest)           │
│  6. Build Docker images                  │
│  7. Push to GHCR                         │
│  8. Create release tag (SemVer)          │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│       GitHub Actions - CD                │
├─────────────────────────────────────────┤
│  1. Decode kubeconfig                    │
│  2. Deploy with Helm                     │
│  3. Verify pod health                    │
│  4. Run smoke tests                      │
│  5. Report deployment status             │
└─────────────────────────────────────────┘
```

### مراحل CI (.github/workflows/ci.yml)

#### 1. Lint و Test برای Backend

```yaml
jobs:
  lint-and-test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
      redis:
        image: redis:7-alpine
    steps:
      - name: Checkout code
      - name: Setup Python 3.11
      - name: Install dependencies
      - name: Run ruff linter
      - name: Run pytest with coverage
```

#### 2. Lint و Test برای Frontend

```yaml
  lint-and-test-frontend:
    runs-on: ubuntu-latest
    steps:
      - name: Setup pnpm
      - name: Install dependencies
      - name: Type check (tsc)
      - name: Run vitest tests
      - name: Build Next.js
```

#### 3. ساخت و Push ایمیج‌های Docker

```yaml
  build-and-push-images:
    needs: [lint-and-test-backend, lint-and-test-frontend]
    steps:
      - name: Login to GHCR
      - name: Build backend image
      - name: Build frontend image
      - name: Push images
```

#### 4. ایجاد Release Tag خودکار

```yaml
  create-release:
    needs: [build-and-push-images]
    steps:
      - name: Get latest tag
      - name: Bump patch version
      - name: Create and push new tag
```

### مراحل CD (.github/workflows/deploy.yml)

```bash
# Trigger: Push به tags با فرمت v*.*.*
# یا اجرای دستی (workflow_dispatch)

# مراحل:
1. Setup kubectl & Helm
2. Configure kubeconfig از KUBECONFIG_B64
3. Deploy با Helm:
   helm upgrade --install docuchat ./infra/chart \
     --set image.backend.tag=$TAG \
     --set image.frontend.tag=$TAG \
     --set secrets.openaiApiKey=$OPENAI_API_KEY
4. Verify deployment health
5. Run smoke tests
6. Generate deployment summary
```

### اجرای دستی Deployment

```bash
# از طریق GitHub UI
Actions → Deploy to Kubernetes → Run workflow → Select environment

# یا از طریق CLI
gh workflow run deploy.yml \
  -f environment=production
```

---

## مانیتورینگ و Observability

### Metrics موجود

DocuChat متریک‌های زیر را در endpoint `/api/v1/metrics` expose می‌کند:

#### 1. متریک‌های OpenAI Token

```prometheus
# مجموع توکن‌های مصرف‌شده
openai_tokens_total{tenant="demo-corp", direction="in", model="gpt-4o"}

# مثال کوئری: توکن‌های مصرفی 24 ساعت گذشته
sum by (tenant) (increase(openai_tokens_total[24h]))
```

#### 2. متریک‌های ML Fallback

```prometheus
# تعداد fallback بین مدل‌ها
ml_fallback_total{from_model="gpt-4o", to_model="gpt-4o-mini", tenant="demo-corp"}

# مثال: نرخ fallback در 5 دقیقه گذشته
rate(ml_fallback_total[5m])
```

#### 3. متریک‌های HTTP Request

```prometheus
# مدت زمان درخواست‌ها (histogram)
http_request_duration_seconds_bucket{method="POST", endpoint="/api/v1/chat", status="200"}

# مثال: P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### 4. متریک‌های OpenAI API

```prometheus
# درخواست‌های OpenAI
openai_request_total{tenant="demo-corp", model="gpt-4o", status="success"}

# زمان پاسخ OpenAI
openai_request_duration_seconds{tenant="demo-corp", model="gpt-4o"}
```

#### 5. متریک‌های RAG

```prometheus
# کوئری‌های RAG
rag_query_total{tenant="demo-corp", model="gpt-4o"}

# تعداد chunk های ذخیره‌شده
document_chunks_total{tenant="demo-corp"}
```

### Prometheus Configuration

**فایل:** `infra/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'docuchat-backend'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: [docuchat-prod]
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
        action: keep
        regex: backend
    metrics_path: /api/v1/metrics
```

### Alert Rules

**فایل:** `infra/prometheus/alerts.yml`

#### هشدارهای مهم:

1. **HighErrorRate**: نرخ خطای 5xx بیش از 5٪
2. **HighLatency**: P95 latency بیش از 2 ثانیه
3. **OpenAIHighFailureRate**: نرخ خطای OpenAI بیش از 10٪
4. **ExcessiveMLFallbacks**: Fallback بیش از 10 بار در ثانیه
5. **PodDown**: Pod از دسترس خارج است
6. **HighMemoryUsage**: استفاده از حافظه بیش از 90٪
7. **TokenConsumptionSpike**: افزایش ناگهانی مصرف توکن (3 برابر)

### Grafana Dashboards

#### Dashboard 1: Backend Overview

**مسیر:** `infra/grafana/dashboards/backend-overview.json`

**پنل‌ها:**
- نرخ درخواست (Request Rate)
- زمان پاسخ (P50, P95, P99)
- نرخ خطا بر اساس کد وضعیت
- تعداد Podهای فعال
- مصرف CPU و Memory

**دسترسی:** http://localhost:3001 (محیط محلی) یا https://grafana.docuchat.example.com

#### Dashboard 2: Token Usage & Billing

**مسیر:** `infra/grafana/dashboards/token-usage.json`

**پنل‌ها:**
- مصرف توکن بر اساس tenant
- مجموع توکن‌های 24 ساعت گذشته
- هزینه تخمینی به تومان
- نمودار Fallback بین مدل‌ها
- مدت زمان درخواست‌های OpenAI
- نرخ موفقیت OpenAI API

### دسترسی به Monitoring Stack

```bash
# Port-forward به Prometheus
kubectl port-forward -n docuchat-prod svc/docuchat-prometheus 9090:9090

# Port-forward به Grafana
kubectl port-forward -n docuchat-prod svc/docuchat-grafana 3000:3000

# لاگین به Grafana
# Username: admin
# Password: $GRAFANA_ADMIN_PASSWORD
```

---

## سیستم صدور صورتحساب

### معماری Billing

```
┌──────────────────────────────────────────────────┐
│         CronJob (Daily at 3:00 AM)               │
├──────────────────────────────────────────────────┤
│  1. Query Prometheus API                         │
│     - Get openai_tokens_total per tenant         │
│     - Calculate 24h increase                     │
│                                                   │
│  2. Calculate Costs                              │
│     - Price: 20 Tomans per 1000 tokens           │
│     - Apply tenant-specific discounts            │
│                                                   │
│  3. Create Invoice Records                       │
│     - Insert into tenant_invoice table           │
│     - Status: 'pending'                          │
│                                                   │
│  4. Generate Payment Links                       │
│     - Call Zibal API                             │
│     - Create payment URL                         │
│                                                   │
│  5. Send Email Notifications                     │
│     - Email invoice to tenant                    │
│     - Include payment link                       │
│                                                   │
│  6. Log Summary                                  │
│     - Total revenue generated                    │
│     - Number of invoices created                 │
└──────────────────────────────────────────────────┘
```

### جدول Database

```sql
CREATE TABLE tenant_invoice (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    tokens BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    zibal_track_id VARCHAR(255),
    paid_at TIMESTAMP NULL
);

CREATE INDEX idx_tenant_invoice_tenant ON tenant_invoice(tenant_id);
CREATE INDEX idx_tenant_invoice_status ON tenant_invoice(status);
```

### قیمت‌گذاری

```python
# هزینه پایه: 20 تومان به ازای هر 1000 توکن
PRICE_PER_1K_TOKENS = 20

# مثال محاسبه
tokens_used = 150000
cost_tomans = (tokens_used / 1000) * PRICE_PER_1K_TOKENS
# = (150000 / 1000) * 20 = 3000 تومان
```

### یکپارچگی با زیبال (Zibal)

```python
# ایجاد درخواست پرداخت
import requests

payload = {
    "merchant": ZIBAL_API_KEY,
    "amount": int(amount * 10),  # تبدیل تومان به ریال
    "callbackUrl": "https://docuchat.example.com/billing/callback",
    "description": f"DocuChat usage for {tenant_id}",
    "orderId": f"{tenant_id}-{date}"
}

response = requests.post(
    "https://gateway.zibal.ir/v1/request",
    json=payload
)

if response.json()["result"] == 100:
    track_id = response.json()["trackId"]
    payment_url = f"https://gateway.zibal.ir/start/{track_id}"
```

### اجرای دستی Billing Job

```bash
# اجرای یک‌بار برای تست
kubectl create job --from=cronjob/docuchat-billing manual-billing-$(date +%s) -n docuchat-prod

# مشاهده لاگ‌ها
kubectl logs -f job/manual-billing-XXXXX -n docuchat-prod

# خروجی نمونه:
# ============================================================
# 🔄 Starting billing job at 2025-10-06 03:00:00
# ============================================================
# 
# 📊 Querying Prometheus for token usage...
# ✅ Found usage for 3 tenant(s)
# 
# Processing tenant: demo-corp
#   Tokens: 150,000
#   Amount: 3,000.00 Tomans
# ✅ Invoice created for tenant demo-corp
# 💳 Payment link created: https://gateway.zibal.ir/start/XXXXX
# 📧 Email sent to demo-corp
# 
# ============================================================
# ✅ Billing job completed
# 💰 Total revenue: 8,450.00 Tomans
# ============================================================
```

### تنظیم زمان اجرا

```yaml
# در values.yaml
billing:
  enabled: true
  schedule: "0 3 * * *"  # هر روز ساعت 03:00

# برای تغییر زمان:
helm upgrade docuchat ./infra/chart \
  --set billing.schedule="0 2 * * *"  # تغییر به ساعت 02:00
```

---

## امنیت و مدیریت Secrets

### ذخیره Secrets در Kubernetes

```bash
# ایجاد Secret
kubectl create secret generic docuchat-secrets \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=ZIBAL_API_KEY='zibal-...' \
  --from-literal=JWT_SECRET='...' \
  --namespace docuchat-prod

# یا از طریق Helm
helm upgrade docuchat ./infra/chart \
  --set secrets.openaiApiKey='sk-...' \
  --set secrets.databaseUrl='postgresql://...'
```

### رمزگذاری Secrets در GitHub Actions

```bash
# تنظیم secret در GitHub
gh secret set OPENAI_API_KEY --body "sk-..." --repo owner/repo

# برای kubeconfig
cat ~/.kube/config | base64 | gh secret set KUBECONFIG_B64 --repo owner/repo
```

### Network Policy

```yaml
# محدود کردن دسترسی شبکه
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: docuchat-backend-policy
spec:
  podSelector:
    matchLabels:
      app: docuchat-backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: docuchat-frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgresql
      ports:
        - protocol: TCP
          port: 5432
```

### چرخش Secrets

به [Runbook چرخش Secrets](../../infra/runbook/rotate-secrets.md) مراجعه کنید.

---

## Disaster Recovery

### سناریوهای بازیابی

#### 1. بازیابی پایگاه داده

به [Runbook بازیابی DB](../../infra/runbook/recovery-db.md) مراجعه کنید.

**خلاصه مراحل:**
```bash
# 1. توقف backend
kubectl scale deployment/docuchat-backend --replicas=0

# 2. بازیابی از backup
pg_restore -d docuchat backup.dump

# 3. راه‌اندازی مجدد
kubectl scale deployment/docuchat-backend --replicas=2
```

#### 2. Rollback Deployment

```bash
# مشاهده تاریخچه
helm history docuchat -n docuchat-prod

# Rollback به نسخه قبلی
helm rollback docuchat -n docuchat-prod

# یا به نسخه خاص
helm rollback docuchat 5 -n docuchat-prod
```

#### 3. بازیابی از Disaster کامل

```bash
# 1. راه‌اندازی cluster جدید
# 2. نصب dependencies (NGINX Ingress, Cert-Manager)
# 3. بازیابی database از backup
# 4. Deploy application با Helm
helm install docuchat ./infra/chart \
  --namespace docuchat-prod \
  --create-namespace \
  -f production-values.yaml

# 5. بازیابی DNS records
# 6. تست کامل عملکرد
```

### Backup خودکار

```yaml
# CronJob برای Backup روزانه
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"  # هر روز ساعت 2 صبح
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgresql -U docuchat docuchat | \
              gzip > /backup/docuchat_$(date +%Y%m%d).sql.gz
```

---

## مقیاس‌پذیری

### Horizontal Pod Autoscaler (HPA)

```yaml
# فعال‌سازی autoscaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: docuchat-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docuchat-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler (VPA)

```bash
# نصب VPA
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh

# ایجاد VPA برای backend
kubectl apply -f - <<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: docuchat-backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docuchat-backend
  updatePolicy:
    updateMode: "Auto"
EOF
```

### Database Scaling

```bash
# افزایش اندازه disk
kubectl patch pvc postgres-data \
  -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'

# یا استفاده از Cloud provider's managed database
# مثال: AWS RDS، Google Cloud SQL، Azure Database
```

### مقیاس‌پذیری GPU

برای مدل‌های سنگین‌تر OpenAI یا embedding محلی، به [Runbook مقیاس‌پذیری GPU](../../infra/runbook/scale-gpu.md) مراجعه کنید.

---

## محیط توسعه محلی

### پیش‌نیازها

```bash
# نصب Docker و Docker Compose
docker --version  # >= 24.0
docker-compose --version  # >= 2.20

# کلون کردن repository
git clone https://github.com/your-org/docuchat.git
cd docuchat
```

### راه‌اندازی با Docker Compose

```bash
# تنظیم متغیرهای محیطی
cp .env.example .env
# ویرایش .env و تنظیم OPENAI_API_KEY

# اجرای تمام سرویس‌ها
cd infra/
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f

# بررسی وضعیت
docker-compose ps
```

### دسترسی به سرویس‌ها

| سرویس | URL | توضیحات |
|--------|-----|---------|
| Frontend | http://localhost:3000 | رابط کاربری |
| Backend API | http://localhost:8000 | API سرور |
| Prometheus | http://localhost:9090 | متریک‌ها |
| Grafana | http://localhost:3001 | داشبوردها (admin/admin) |
| PostgreSQL | localhost:5432 | دیتابیس |
| Redis | localhost:6379 | کش |

### تست API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Metrics
curl http://localhost:8000/api/v1/metrics

# ثبت‌نام کاربر جدید
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# دریافت token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@example.com&password=password123"
```

### توقف سرویس‌ها

```bash
# توقف موقت
docker-compose stop

# حذف کانتینرها (حفظ data)
docker-compose down

# حذف کامل (شامل volumes)
docker-compose down -v
```

---

## دستورات Makefile

**فایل:** `Makefile`

```makefile
.PHONY: devops-up devops-down devops-check devops-logs

# راه‌اندازی محیط توسعه
devops-up:
	cd infra && docker-compose up -d
	@echo "✅ Services started"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin)"

# توقف سرویس‌ها
devops-down:
	cd infra && docker-compose down

# بررسی سلامت سرویس‌ها
devops-check:
	@echo "Checking service health..."
	@curl -sf http://localhost:8000/api/v1/health || echo "❌ Backend unhealthy"
	@curl -sf http://localhost:9090/-/healthy || echo "❌ Prometheus unhealthy"
	@curl -sf http://localhost:3001/api/health || echo "❌ Grafana unhealthy"
	@echo "✅ All services healthy"

# مشاهده لاگ‌ها
devops-logs:
	cd infra && docker-compose logs -f

# اجرای تست‌ها
test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && pnpm test

# Lint
lint:
	cd backend && ruff check app/
	cd frontend && pnpm exec tsc --noEmit
```

**استفاده:**

```bash
# راه‌اندازی
make devops-up

# بررسی سلامت
make devops-check

# مشاهده لاگ‌ها
make devops-logs

# توقف
make devops-down
```

---

## نکات مهم

### 1. امنیت

- ✅ همیشه از HTTPS استفاده کنید
- ✅ Secret‌ها را هرگز در کد commit نکنید
- ✅ Network Policy را فعال کنید
- ✅ Secret‌ها را به‌طور دوره‌ای rotate کنید
- ✅ از 2FA برای دسترسی‌های مهم استفاده کنید

### 2. Monitoring

- ✅ Alert‌ها را به‌طور منظم بررسی کنید
- ✅ Dashboard‌ها را روزانه چک کنید
- ✅ SLO/SLA را تعریف و پیگیری کنید
- ✅ Incident response plan داشته باشید

### 3. Cost Optimization

- ✅ از autoscaling استفاده کنید
- ✅ Resource limits مشخص کنید
- ✅ Idle resources را حذف کنید
- ✅ از spot/preemptible instances استفاده کنید

### 4. Backup

- ✅ Backup‌های خودکار روزانه
- ✅ Backup‌ها را تست کنید
- ✅ Retention policy مشخص کنید
- ✅ Backup‌ها را در مکان جداگانه ذخیره کنید

---

## منابع و مستندات

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Zibal Payment Gateway](https://docs.zibal.ir/)

---

## پشتیبانی

- **تیم DevOps**: devops@docuchat.io
- **نفربر آماده‌باش**: oncall@docuchat.io
- **مستندات داخلی**: https://docs.docuchat.io
- **Repository**: https://github.com/your-org/docuchat

---

**نسخه:** 1.0.0  
**آخرین به‌روزرسانی:** 2025-10-06  
**نگهدارنده:** تیم DevOps DocuChat
