# Database Recovery Runbook

## Overview
This runbook provides step-by-step instructions for recovering the DocuChat PostgreSQL database from backups.

## Prerequisites
- Access to Kubernetes cluster with appropriate permissions
- kubectl configured with correct context
- Database backup files or snapshots available

## Recovery Scenarios

### Scenario 1: Restore from pg_dump Backup

#### Step 1: Stop Application Pods
```bash
# Scale down backend to prevent new connections
kubectl scale deployment docuchat-backend -n docuchat-prod --replicas=0

# Wait for pods to terminate
kubectl wait --for=delete pod -l app.kubernetes.io/component=backend -n docuchat-prod --timeout=60s
```

#### Step 2: Access Database Pod
```bash
# Port-forward to database service
kubectl port-forward svc/postgresql -n docuchat-prod 5432:5432 &
PF_PID=$!
```

#### Step 3: Drop and Recreate Database
```bash
# Connect to postgres admin database
psql -h localhost -U docuchat -d postgres

# Drop existing database
DROP DATABASE IF EXISTS docuchat;

# Create fresh database
CREATE DATABASE docuchat;

# Enable pgvector extension
\c docuchat
CREATE EXTENSION IF NOT EXISTS vector;

\q
```

#### Step 4: Restore from Backup
```bash
# Restore from backup file
pg_restore -h localhost -U docuchat -d docuchat \
  --clean --if-exists --no-owner --no-acl \
  /path/to/backup/docuchat_backup_YYYYMMDD.dump

# Or from SQL dump
psql -h localhost -U docuchat -d docuchat < /path/to/backup/docuchat_backup_YYYYMMDD.sql
```

#### Step 5: Verify Data Integrity
```bash
# Connect and check tables
psql -h localhost -U docuchat -d docuchat

# Verify critical tables exist
\dt

# Check record counts
SELECT 'tenants' as table_name, COUNT(*) FROM tenants
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'chunks', COUNT(*) FROM chunks;

\q
```

#### Step 6: Restart Application
```bash
# Kill port-forward
kill $PF_PID

# Scale backend back up
kubectl scale deployment docuchat-backend -n docuchat-prod --replicas=2

# Monitor rollout
kubectl rollout status deployment/docuchat-backend -n docuchat-prod
```

#### Step 7: Smoke Test
```bash
# Test health endpoint
kubectl port-forward svc/docuchat-backend -n docuchat-prod 8000:8000 &
PF_PID=$!

curl http://localhost:8000/api/v1/health

kill $PF_PID
```

---

### Scenario 2: Restore from Volume Snapshot

#### Step 1: List Available Snapshots
```bash
# For cloud providers (example: AWS EBS)
aws ec2 describe-snapshots \
  --owner-ids self \
  --filters "Name=tag:Application,Values=docuchat" \
  --query 'Snapshots[*].[SnapshotId,StartTime,Description]' \
  --output table
```

#### Step 2: Create PVC from Snapshot
```yaml
# Create snapshot-restore-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data-restore
  namespace: docuchat-prod
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  dataSource:
    name: snapshot-XXXXXXXX  # Replace with snapshot ID
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

```bash
kubectl apply -f snapshot-restore-pvc.yaml
```

#### Step 3: Deploy Test Database Pod
```yaml
# Create test-db-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: postgres-test
  namespace: docuchat-prod
spec:
  containers:
  - name: postgres
    image: pgvector/pgvector:pg16
    env:
    - name: POSTGRES_PASSWORD
      value: "temp-password"
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-data-restore
```

```bash
kubectl apply -f test-db-pod.yaml
kubectl wait --for=condition=ready pod/postgres-test -n docuchat-prod --timeout=120s
```

#### Step 4: Verify Restored Data
```bash
kubectl exec -it postgres-test -n docuchat-prod -- psql -U docuchat -d docuchat -c "SELECT COUNT(*) FROM users;"
```

#### Step 5: Swap PVC
```bash
# Scale down production database
kubectl scale statefulset postgresql -n docuchat-prod --replicas=0

# Update StatefulSet to use restored PVC
kubectl edit statefulset postgresql -n docuchat-prod
# Change persistentVolumeClaim name to postgres-data-restore

# Scale back up
kubectl scale statefulset postgresql -n docuchat-prod --replicas=1
```

---

## Automated Backup Script

```bash
#!/bin/bash
# backup-db.sh

NAMESPACE="docuchat-prod"
BACKUP_DIR="/backups/docuchat"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/docuchat_backup_$TIMESTAMP.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Port-forward to database
kubectl port-forward svc/postgresql -n $NAMESPACE 5432:5432 &
PF_PID=$!
sleep 3

# Create backup
pg_dump -h localhost -U docuchat docuchat > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

# Kill port-forward
kill $PF_PID

echo "Backup completed: ${BACKUP_FILE}.gz"
```

## Scheduled Backup CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: docuchat-prod
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
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
              pg_dump -h postgresql -U docuchat docuchat | gzip > /backup/docuchat_$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: docuchat-secrets
                  key: DATABASE_PASSWORD
            volumeMounts:
            - name: backup
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: postgres-backups
```

## Monitoring & Alerts

### Backup Verification
```bash
# Verify backup exists and is recent
ls -lh /backups/docuchat/ | tail -5

# Check backup file size (should be > 1MB)
du -sh /backups/docuchat/docuchat_backup_*.sql.gz
```

### Alert on Backup Failure
Add to Prometheus alerts:
```yaml
- alert: DatabaseBackupFailed
  expr: time() - kube_job_status_succeeded{job_name=~"postgres-backup.*"} > 86400
  labels:
    severity: critical
  annotations:
    summary: "Database backup has not succeeded in 24 hours"
```

## Contact & Escalation

- **Database Team**: dba@docuchat.io
- **On-call Engineer**: oncall@docuchat.io
- **Escalation**: CTO if recovery takes > 2 hours

## Post-Recovery Checklist

- [ ] Verify all tables exist and have expected row counts
- [ ] Check pgvector extension is enabled
- [ ] Test user authentication
- [ ] Test document upload and retrieval
- [ ] Verify RAG query functionality
- [ ] Monitor error rates in Grafana
- [ ] Update incident documentation
