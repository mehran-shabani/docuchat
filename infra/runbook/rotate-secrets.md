# Secret Rotation Runbook

## Overview
This runbook provides procedures for rotating compromised or expired secrets in the DocuChat application.

## Secret Types

1. **OpenAI API Key** - Most critical, affects all AI functionality
2. **Zibal API Key** - Payment gateway credentials
3. **JWT Secret** - Authentication token signing
4. **Database Password** - PostgreSQL access
5. **Redis Password** - Cache access
6. **Grafana Admin Password** - Monitoring dashboard

---

## Emergency: OpenAI API Key Compromised

### Immediate Actions (< 5 minutes)

#### Step 1: Revoke Compromised Key
```bash
# Go to OpenAI dashboard and immediately revoke the key
# https://platform.openai.com/api-keys

# Or use API (if available)
curl -X DELETE https://api.openai.com/v1/api-keys/sk-XXXXX \
  -H "Authorization: Bearer $OPENAI_MASTER_KEY"
```

#### Step 2: Generate New Key
```bash
# Generate new key from OpenAI dashboard
# Save to secure location temporarily
NEW_OPENAI_KEY="sk-new-key-here"
```

#### Step 3: Update Kubernetes Secret
```bash
# Update secret in cluster
kubectl create secret generic docuchat-secrets \
  --from-literal=OPENAI_API_KEY="$NEW_OPENAI_KEY" \
  --namespace docuchat-prod \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secret updated
kubectl get secret docuchat-secrets -n docuchat-prod -o jsonpath='{.data.OPENAI_API_KEY}' | base64 -d | head -c 10
```

#### Step 4: Rolling Restart
```bash
# Restart backend pods to pick up new secret
kubectl rollout restart deployment/docuchat-backend -n docuchat-prod

# Monitor rollout
kubectl rollout status deployment/docuchat-backend -n docuchat-prod --timeout=5m
```

#### Step 5: Verify Functionality
```bash
# Test OpenAI endpoint
kubectl port-forward svc/docuchat-backend -n docuchat-prod 8000:8000 &
PF_PID=$!

# Make test request
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer $TEST_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "test"}]
  }'

kill $PF_PID
```

#### Step 6: Update GitHub Secrets
```bash
# Using GitHub CLI
gh secret set OPENAI_API_KEY --body "$NEW_OPENAI_KEY" --repo owner/repo

# Or via UI: Settings > Secrets and variables > Actions
```

### Post-Incident Actions (< 24 hours)

1. **Audit Access Logs**
   ```bash
   # Check OpenAI usage logs for unauthorized usage
   # https://platform.openai.com/usage
   
   # Export logs for analysis
   curl https://api.openai.com/v1/usage \
     -H "Authorization: Bearer $NEW_OPENAI_KEY" > usage_audit.json
   ```

2. **Review Application Logs**
   ```bash
   # Check for failed requests during rotation
   kubectl logs -l app.kubernetes.io/component=backend \
     -n docuchat-prod \
     --since=1h | grep -i "openai\|unauthorized\|401"
   ```

3. **Update Documentation**
   - Record incident in incident log
   - Update key rotation timestamp
   - Review access control policies

---

## JWT Secret Rotation

### Step 1: Generate New Secret
```bash
# Generate cryptographically secure secret
NEW_JWT_SECRET=$(openssl rand -base64 32)
echo "New JWT Secret: $NEW_JWT_SECRET"
```

### Step 2: Deploy with Both Secrets (Zero-Downtime)
```bash
# Update application to accept BOTH old and new secrets for validation
# Deploy updated code first

# Then update secret
kubectl patch secret docuchat-secrets -n docuchat-prod \
  --type='json' \
  -p='[{"op": "replace", "path": "/data/JWT_SECRET", "value": "'$(echo -n $NEW_JWT_SECRET | base64)'"}]'

# Rolling restart
kubectl rollout restart deployment/docuchat-backend -n docuchat-prod
```

### Step 3: Monitor Active Sessions
```bash
# Wait for old tokens to expire (default: 24 hours)
# Monitor error rates for authentication failures

kubectl logs -f deployment/docuchat-backend -n docuchat-prod | grep "jwt\|authentication"
```

### Step 4: Remove Old Secret Support
```bash
# After token expiry period, deploy code that only accepts new secret
# This completes the rotation
```

---

## Database Password Rotation

### Step 1: Create New Password
```bash
NEW_DB_PASSWORD=$(openssl rand -base64 24)
```

### Step 2: Update PostgreSQL
```bash
# Port-forward to database
kubectl port-forward svc/postgresql -n docuchat-prod 5432:5432 &
PF_PID=$!

# Update password
psql -h localhost -U postgres -c "ALTER USER docuchat WITH PASSWORD '$NEW_DB_PASSWORD';"

kill $PF_PID
```

### Step 3: Update Application Secret
```bash
# Update DATABASE_URL with new password
OLD_DB_URL=$(kubectl get secret docuchat-secrets -n docuchat-prod -o jsonpath='{.data.DATABASE_URL}' | base64 -d)
NEW_DB_URL=$(echo "$OLD_DB_URL" | sed "s/:.*@/:$NEW_DB_PASSWORD@/")

kubectl patch secret docuchat-secrets -n docuchat-prod \
  --type='json' \
  -p='[{"op": "replace", "path": "/data/DATABASE_URL", "value": "'$(echo -n $NEW_DB_URL | base64)'"}]'
```

### Step 4: Restart Application
```bash
kubectl rollout restart deployment/docuchat-backend -n docuchat-prod
kubectl rollout status deployment/docuchat-backend -n docuchat-prod
```

---

## Zibal API Key Rotation

### Step 1: Get New Key from Zibal
```bash
# Login to Zibal merchant dashboard
# Navigate to API Keys section
# Generate new key
NEW_ZIBAL_KEY="zibal-new-key-here"
```

### Step 2: Update Secret
```bash
kubectl patch secret docuchat-secrets -n docuchat-prod \
  --type='json' \
  -p='[{"op": "replace", "path": "/data/ZIBAL_API_KEY", "value": "'$(echo -n $NEW_ZIBAL_KEY | base64)'"}]'
```

### Step 3: Restart Billing CronJob
```bash
# No restart needed - CronJob will pick up new secret on next run
# Verify secret is correct
kubectl get secret docuchat-secrets -n docuchat-prod -o jsonpath='{.data.ZIBAL_API_KEY}' | base64 -d
```

### Step 4: Test Manually
```bash
# Trigger manual billing job to verify
kubectl create job --from=cronjob/docuchat-billing manual-billing-test -n docuchat-prod

# Check logs
kubectl logs job/manual-billing-test -n docuchat-prod
```

---

## Grafana Admin Password Rotation

### Step 1: Generate New Password
```bash
NEW_GRAFANA_PASSWORD=$(openssl rand -base64 16)
```

### Step 2: Update Grafana
```bash
# Port-forward to Grafana
kubectl port-forward svc/grafana -n docuchat-prod 3000:3000 &
PF_PID=$!

# Update via API
curl -X PUT http://admin:$OLD_GRAFANA_PASSWORD@localhost:3000/api/admin/users/1/password \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"$NEW_GRAFANA_PASSWORD\"}"

kill $PF_PID
```

### Step 3: Update Secret
```bash
kubectl patch secret docuchat-secrets -n docuchat-prod \
  --type='json' \
  -p='[{"op": "replace", "path": "/data/GRAFANA_ADMIN_PASSWORD", "value": "'$(echo -n $NEW_GRAFANA_PASSWORD | base64)'"}]'
```

---

## Automated Secret Rotation Schedule

| Secret | Rotation Frequency | Owner | Last Rotated |
|--------|-------------------|-------|--------------|
| OpenAI API Key | 90 days (or on compromise) | Security Team | YYYY-MM-DD |
| JWT Secret | 180 days | Backend Team | YYYY-MM-DD |
| Database Password | 90 days | DBA Team | YYYY-MM-DD |
| Zibal API Key | Annually | Finance Team | YYYY-MM-DD |
| Grafana Password | 90 days | DevOps Team | YYYY-MM-DD |

---

## Secret Management Best Practices

### 1. Use External Secret Management (Recommended)
```yaml
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Example: AWS Secrets Manager integration
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secretsmanager
  namespace: docuchat-prod
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: docuchat-secrets
  namespace: docuchat-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: docuchat-secrets
    creationPolicy: Owner
  data:
    - secretKey: OPENAI_API_KEY
      remoteRef:
        key: docuchat/prod/openai-key
```

### 2. Enable Secret Encryption at Rest
```bash
# Verify encryption is enabled
kubectl get secrets -n docuchat-prod -o json | jq '.items[0].metadata'
```

### 3. Audit Secret Access
```bash
# Enable audit logging for secret access
# Check kube-apiserver audit logs
kubectl logs -n kube-system kube-apiserver-XXX | grep "secrets.*docuchat-secrets"
```

### 4. Implement Secret Scanning
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

---

## Emergency Contacts

- **Security Team**: security@docuchat.io
- **On-call Engineer**: oncall@docuchat.io  
- **OpenAI Support**: https://help.openai.com
- **Zibal Support**: support@zibal.ir

## Post-Rotation Checklist

- [ ] Secret rotated in production
- [ ] Secret updated in GitHub Actions
- [ ] Application restarted and verified
- [ ] No errors in logs
- [ ] Old secret revoked/disabled
- [ ] Rotation documented
- [ ] Team notified
- [ ] Monitoring alerts reviewed
