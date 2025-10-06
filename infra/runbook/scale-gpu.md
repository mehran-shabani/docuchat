# GPU Scaling Runbook

## Overview
This runbook provides guidance for scaling GPU resources when DocuChat needs to support heavier OpenAI models or increased workload.

**Note**: DocuChat currently uses OpenAI's hosted API, which doesn't require local GPU resources. This guide is for future scenarios where you might:
- Host embedding models locally
- Run inference workers for model fine-tuning
- Deploy local LLM alternatives as fallbacks

---

## When to Scale GPU Resources

### Indicators
- ✅ Average RAG query latency > 5 seconds
- ✅ Embedding generation queue length > 100
- ✅ CPU-based embedding generation saturating cores
- ✅ Planning to fine-tune custom models
- ✅ Implementing local model fallback strategy

### Cost-Benefit Analysis
```
GPU Node Cost:     ~$500-2000/month (cloud)
OpenAI API Cost:   Variable based on usage

Break-even point: ~500,000+ embeddings/month
```

---

## Architecture Options

### Option 1: Dedicated Embedding Worker (Recommended)

Deploy separate GPU-enabled pods for embedding generation only.

```yaml
# embedding-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docuchat-embedding-worker
  namespace: docuchat-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: embedding-worker
  template:
    metadata:
      labels:
        app: embedding-worker
    spec:
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-tesla-t4
      containers:
      - name: worker
        image: docuchat/embedding-worker:latest
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "4"
          requests:
            nvidia.com/gpu: 1
            memory: "4Gi"
            cpu: "2"
        env:
        - name: MODEL_NAME
          value: "sentence-transformers/all-mpnet-base-v2"
        - name: BATCH_SIZE
          value: "32"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: docuchat-secrets
              key: REDIS_URL
```

### Option 2: Hybrid Backend with GPU Support

Add GPU support to existing backend pods for specific endpoints.

```yaml
# backend-gpu-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docuchat-backend-gpu
  namespace: docuchat-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend-gpu
  template:
    metadata:
      labels:
        app: backend-gpu
    spec:
      nodeSelector:
        gpu-enabled: "true"
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      containers:
      - name: backend
        image: docuchat/backend-gpu:latest
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "8"
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "4"
```

---

## Step-by-Step Scaling Procedure

### Phase 1: Provision GPU Nodes

#### AWS (EKS)
```bash
# Create GPU nodegroup
eksctl create nodegroup \
  --cluster docuchat-prod \
  --name gpu-workers \
  --node-type p3.2xlarge \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 5 \
  --node-labels workload=gpu \
  --node-taints nvidia.com/gpu=true:NoSchedule
```

#### GCP (GKE)
```bash
# Create GPU node pool
gcloud container node-pools create gpu-pool \
  --cluster docuchat-prod \
  --zone us-central1-a \
  --machine-type n1-standard-4 \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --num-nodes 2 \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autoscaling \
  --node-labels gpu=true
```

#### Azure (AKS)
```bash
# Create GPU node pool
az aks nodepool add \
  --resource-group docuchat-rg \
  --cluster-name docuchat-prod \
  --name gpupool \
  --node-count 2 \
  --node-vm-size Standard_NC6 \
  --labels gpu=true \
  --node-taints sku=gpu:NoSchedule
```

### Phase 2: Install NVIDIA Device Plugin

```bash
# Install NVIDIA device plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# Verify GPU is available
kubectl get nodes -o json | jq '.items[].status.capacity."nvidia.com/gpu"'
```

### Phase 3: Deploy GPU-Enabled Application

#### Option A: Embedding Worker
```bash
# Build embedding worker image
cd backend/
docker build -f Dockerfile.embedding-worker -t docuchat/embedding-worker:v1 .

# Push to registry
docker push docuchat/embedding-worker:v1

# Deploy
kubectl apply -f embedding-worker-deployment.yaml

# Verify deployment
kubectl get pods -l app=embedding-worker -n docuchat-prod
kubectl logs -l app=embedding-worker -n docuchat-prod --tail=50
```

#### Option B: Update Backend Service
```bash
# Update backend to use GPU for specific operations
helm upgrade docuchat ./infra/chart \
  --namespace docuchat-prod \
  --set gpu.enabled=true \
  --set gpu.nodeSelector."cloud\.google\.com/gke-accelerator"=nvidia-tesla-t4 \
  --set resources.backend.limits."nvidia\.com/gpu"=1
```

### Phase 4: Configure Application

#### Update Backend to Use Local Embeddings
```python
# app/services/embedder.py

import os
from typing import List
import torch
from sentence_transformers import SentenceTransformer

class GPUEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(
            'sentence-transformers/all-mpnet-base-v2',
            device=self.device
        )
        print(f"Embedder initialized on device: {self.device}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local GPU model"""
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()

# Use in RAG pipeline
embedder = GPUEmbedder()
```

#### Environment Configuration
```yaml
# values.yaml updates
gpu:
  enabled: true
  embedder:
    model: "sentence-transformers/all-mpnet-base-v2"
    batchSize: 32
    workers: 2
  resources:
    limits:
      nvidia.com/gpu: 1
      memory: "8Gi"
      cpu: "4"
```

### Phase 5: Monitor Performance

```bash
# Monitor GPU utilization
kubectl exec -it <embedding-worker-pod> -n docuchat-prod -- nvidia-smi

# Or install DCGM exporter for Prometheus
kubectl create -f https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/dcgm-exporter.yaml

# Add to Grafana dashboard
```

---

## Performance Tuning

### Batch Size Optimization
```python
# Test different batch sizes
BATCH_SIZES = [8, 16, 32, 64, 128]

for batch_size in BATCH_SIZES:
    start = time.time()
    embeddings = embedder.embed_texts(texts, batch_size=batch_size)
    duration = time.time() - start
    print(f"Batch size {batch_size}: {duration:.2f}s")
```

### Multi-GPU Support
```yaml
# For multiple GPUs
resources:
  limits:
    nvidia.com/gpu: 2  # Use 2 GPUs
    
# In application code
devices = [0, 1]  # Use GPU 0 and 1
```

### Mixed Precision
```python
# Enable mixed precision for faster inference
model.half()  # Use FP16
embeddings = model.encode(texts, convert_to_tensor=True, precision='float16')
```

---

## Autoscaling GPU Workloads

### Horizontal Pod Autoscaler (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: embedding-worker-hpa
  namespace: docuchat-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: docuchat-embedding-worker
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: embedding_queue_length
      target:
        type: AverageValue
        averageValue: "50"
```

### Cluster Autoscaler
```bash
# Enable cluster autoscaler for GPU nodes
kubectl annotate deployment cluster-autoscaler \
  -n kube-system \
  cluster-autoscaler.kubernetes.io/safe-to-evict="false"
```

---

## Cost Optimization

### 1. Use Spot/Preemptible Instances
```bash
# GKE example
gcloud container node-pools create gpu-spot \
  --cluster docuchat-prod \
  --preemptible \
  --machine-type n1-standard-4 \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --num-nodes 2
```

### 2. Scale to Zero During Off-Hours
```yaml
# CronJob to scale down at night
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-gpu
spec:
  schedule: "0 22 * * *"  # 10 PM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl
            command:
            - kubectl
            - scale
            - deployment/docuchat-embedding-worker
            - --replicas=0
            - -n
            - docuchat-prod
```

### 3. Monitor Cost per Embedding
```promql
# Add metric to track cost efficiency
cost_per_embedding = (gpu_node_cost_per_hour / embeddings_generated_per_hour)
```

---

## Rollback Procedure

If GPU scaling introduces issues:

```bash
# Step 1: Scale GPU workers to 0
kubectl scale deployment/docuchat-embedding-worker --replicas=0 -n docuchat-prod

# Step 2: Revert backend to use OpenAI embeddings
helm upgrade docuchat ./infra/chart \
  --namespace docuchat-prod \
  --set gpu.enabled=false

# Step 3: Delete GPU node pool (optional)
gcloud container node-pools delete gpu-pool --cluster docuchat-prod

# Step 4: Monitor for errors
kubectl logs -f deployment/docuchat-backend -n docuchat-prod
```

---

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver on node
kubectl exec -it <pod-name> -- nvidia-smi

# Check device plugin
kubectl get daemonset -n kube-system | grep nvidia

# Check node labels
kubectl get nodes -L gpu,accelerator
```

### Out of Memory Errors
```bash
# Reduce batch size
# Increase GPU memory limit
# Enable gradient checkpointing

# Monitor GPU memory
kubectl exec -it <pod> -- watch -n 1 nvidia-smi
```

### Slow Performance
```bash
# Check GPU utilization
# Verify CUDA version compatibility
# Profile model inference

# Use NVIDIA profiler
nsys profile python app.py
```

---

## Future Considerations

### Model Fine-Tuning Pipeline
```yaml
# Reserved GPU capacity for training jobs
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-training-quota
spec:
  hard:
    requests.nvidia.com/gpu: "4"
    limits.nvidia.com/gpu: "4"
```

### Multi-Model Serving
```bash
# Deploy model server (e.g., NVIDIA Triton)
helm install triton-server nvidia/triton-inference-server \
  --set image.tag=23.10-py3 \
  --set resources.limits."nvidia\.com/gpu"=2
```

---

## Contact & Support

- **ML/AI Team**: ml@docuchat.io
- **DevOps Team**: devops@docuchat.io
- **NVIDIA Support**: https://developer.nvidia.com/support
- **Cloud Provider Support**: Your cloud provider's support portal
