# VVP Platform - One-Click Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/micpward1980/vvp-platform/tree/devin/1757471412-simple-deployment)

## Quick Deploy (1 Click!)

1. **Click the "Deploy to Render" button above**
2. **Sign up with GitHub** (if you haven't already)
3. **Click "Create Web Service"** 
4. **Wait 5-10 minutes** for deployment
5. **Your VVP platform will be live!**

## What You Get

- **Permanent public URL** that stays online 24/7
- **All 6 microservices** running in one container
- **Web UI** for testing claims
- **Free hosting** on Render's free tier

## Testing Your Deployment

Once deployed, test with these VINs:
- **VIN ending in "1"**: Clean history → ESCALATED status, $0 payout
- **VIN ending in "0"**: Hail damage → PAID status, with payout amount

## Alternative: Manual Deploy

If the button doesn't work:
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect this repository: `micpward1980/vvp-platform`
5. Select branch: `devin/1757471412-simple-deployment`
6. Render will auto-detect the Dockerfile and deploy

---

## About VVP Platform

A comprehensive microservices platform for processing vehicle insurance claims with automated verification, valuation, and payment processing.

## Architecture

The VVP platform consists of 6 FastAPI microservices:

- **claims-orchestrator**: Orchestrates the complete claims workflow (verification → valuation → payment)
- **verification-service**: Validates claims and calculates fraud scores
- **valuation-service**: Calculates vehicle valuations with dual-cap formula
- **payment-service**: Processes payments with idempotency
- **vin-monitor**: Monitors VINs for theft/total-loss scenarios
- **audit-service**: Logs all events for compliance and tracking

## Local Development

### Prerequisites
- Python 3.11+
- Docker
- kubectl (for cluster testing)

### Running Services Locally

1. **Install dependencies for each service:**
```bash
cd services/claims-orchestrator
pip install -r requirements.txt
```

2. **Start services on different ports:**
```bash
# Terminal 1 - Verification Service
cd services/verification-service
uvicorn src.main:app --host 0.0.0.0 --port 8001

# Terminal 2 - Valuation Service  
cd services/valuation-service
uvicorn src.main:app --host 0.0.0.0 --port 8002

# Terminal 3 - Payment Service
cd services/payment-service
uvicorn src.main:app --host 0.0.0.0 --port 8003

# Terminal 4 - VIN Monitor
cd services/vin-monitor
uvicorn src.main:app --host 0.0.0.0 --port 8004

# Terminal 5 - Audit Service
cd services/audit-service
uvicorn src.main:app --host 0.0.0.0 --port 8005

# Terminal 6 - Claims Orchestrator
cd services/claims-orchestrator
ORCH_VERIFICATION_URL=http://localhost:8001 \
ORCH_VALUATION_URL=http://localhost:8002 \
ORCH_PAYMENT_URL=http://localhost:8003 \
ORCH_AUDIT_URL=http://localhost:8005 \
ORCH_VIN_URL=http://localhost:8004 \
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

3. **Test the complete workflow:**
```bash
curl -X POST http://localhost:8000/claims \
  -H "Content-Type: application/json" \
  -d '{
    "policyId": "P-1001",
    "holderName": "Alex Driver", 
    "vin": "1HGCM82633A004352",
    "lossDate": "2025-09-01T12:00:00Z",
    "lossType": "hail",
    "details": "Hail dents"
  }'
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster with kubectl configured
- Helm 3.x
- GitLab CI/CD with Container Registry enabled

### Deploy to Cluster

1. **Configure GitLab CI/CD variables:**
   - `KUBE_CONFIG_B64`: Base64-encoded kubeconfig file

2. **Push to GitLab and trigger pipeline:**
```bash
git push origin main
```

3. **Monitor deployment:**
```bash
kubectl -n vvp get pods
kubectl -n vvp get svc
```

### Testing Deployed Services

1. **Port-forward claims orchestrator:**
```bash
kubectl port-forward -n vvp svc/claims-orchestrator 8080:80
```

2. **Submit test claim:**
```bash
curl -X POST http://localhost:8080/claims \
  -H "Content-Type: application/json" \
  -d '{
    "policyId": "P-1001",
    "holderName": "Alex Driver",
    "vin": "1HGCM82633A004352", 
    "lossDate": "2025-09-01T12:00:00Z",
    "lossType": "hail",
    "details": "Hail dents"
  }'
```

3. **Check audit logs:**
```bash
kubectl port-forward -n vvp svc/audit-service 8081:80
curl http://localhost:8081/audit
```

## API Endpoints

### Claims Orchestrator
- `POST /claims` - Submit new claim
- `GET /claims/{claimId}` - Get claim status
- `GET /health` - Health check

### Verification Service
- `POST /verify` - Verify claim details
- `GET /health` - Health check

### Valuation Service  
- `POST /valuate` - Calculate vehicle valuation
- `GET /health` - Health check

### Payment Service
- `POST /pay` - Process payment
- `GET /health` - Health check

### VIN Monitor
- `POST /monitor/start` - Start VIN monitoring
- `GET /monitor/list` - List monitored VINs
- `GET /health` - Health check

### Audit Service
- `POST /audit` - Log audit event
- `GET /audit` - Get all audit logs
- `GET /audit/claim/{claimId}` - Get logs for specific claim
- `GET /health` - Health check

## Configuration

### Environment Variables

- `ORCH_VERIFICATION_URL`: Verification service URL
- `ORCH_VALUATION_URL`: Valuation service URL  
- `ORCH_PAYMENT_URL`: Payment service URL
- `ORCH_AUDIT_URL`: Audit service URL
- `ORCH_VIN_URL`: VIN monitor service URL

### Helm Values

Key configuration in `charts/vvp-platform/values.yaml`:

```yaml
replicas:
  claimsOrchestrator: 2
  verificationService: 2
  valuationService: 2
  paymentService: 2
  vinMonitor: 1
  auditService: 1

images:
  claimsOrchestrator: { repository: "registry/claims-orchestrator", tag: "latest" }
  # ... other services
```

## Development Workflow

1. Make changes to service code
2. Test locally using the local development setup
3. Commit and push to feature branch
4. Create Merge Request
5. CI pipeline builds, tests, and deploys automatically
6. Verify deployment in cluster

## Troubleshooting

### Common Issues

1. **Service connection errors**: Check environment variables are set correctly
2. **Port conflicts**: Ensure each service runs on a different port locally
3. **Kubernetes deployment fails**: Verify KUBE_CONFIG_B64 is set correctly
4. **CI pipeline fails**: Check GitLab Container Registry is enabled

### Logs

```bash
# Local logs
uvicorn src.main:app --log-level debug

# Kubernetes logs
kubectl -n vvp logs -f deployment/claims-orchestrator
```
