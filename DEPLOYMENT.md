# VVP Platform Deployment Guide

## Current Status ✅
- **Code**: All 6 microservices implemented and tested locally
- **Git**: Branch `devin/vvp-bootstrap` pushed to GitLab successfully
- **GitLab**: Ready for merge request creation
- **CI/CD**: Pipeline configured for lint → test → build → push → deploy

## Next Steps

### 1. Create Merge Request
Visit: https://gitlab.com/micpward-group/vvp-platfom/-/merge_requests/new?merge_request%5Bsource_branch%5D=devin%2Fvvp-bootstrap

**MR Details:**
- Title: VVP Platform Implementation - 6 FastAPI Microservices with Helm & CI/CD
- Source: devin/vvp-bootstrap
- Target: main
- Description: Complete VVP platform with 6 microservices, Helm charts, and GitLab CI/CD pipeline

### 2. Configure CI/CD Variables
In GitLab project → Settings → CI/CD → Variables:

**Required Variable:**
- Key: `KUBE_CONFIG_B64`
- Value: [Base64-encoded kubeconfig from `cat ~/.kube/config | base64`]
- Type: Variable
- Flags: Masked, Protected

### 3. Trigger Deployment Pipeline
Once MR is created and KUBE_CONFIG_B64 is set:
1. Merge the MR to main branch
2. Pipeline will automatically trigger: lint → test → build → push → deploy
3. Monitor at: https://gitlab.com/micpward-group/vvp-platfom/-/pipelines

### 4. Verify Deployment
```bash
# Check pods and services
kubectl -n vvp get pods
kubectl -n vvp get svc

# Expected output: 6 deployments with 2+ replicas each
# - claims-orchestrator (2 replicas)
# - verification-service (2 replicas) 
# - valuation-service (2 replicas)
# - payment-service (2 replicas)
# - vin-monitor (1 replica)
# - audit-service (1 replica)
```

### 5. Test Claims API
```bash
# Port-forward claims orchestrator
kubectl port-forward -n vvp svc/claims-orchestrator 8080:80

# Submit test claim (in new terminal)
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

# Expected response: JSON with claimId and status "PAID"
```

### 6. Check Audit Logs
```bash
# Port-forward audit service
kubectl port-forward -n vvp svc/audit-service 8081:80

# Get last 5 audit entries
curl http://localhost:8081/audit | jq '.[-5:]'
```

## Pipeline Stages

### Stage 1: Lint (< 1 min)
- Validates directory structure
- Checks for required Dockerfiles
- Verifies all services have main.py files

### Stage 2: Test (< 2 min)
- Installs Python dependencies
- Runs smoke tests on all service files
- Validates FastAPI app imports

### Stage 3: Build (5-8 min)
- Builds Docker images for all 6 services
- Tags with commit SHA: `$CI_REGISTRY_IMAGE/<service>:$CI_COMMIT_SHA`
- Stores image tags as artifacts

### Stage 4: Push (2-3 min)
- Pushes all Docker images to GitLab Container Registry
- Images available at: `registry.gitlab.com/micpward-group/vvp-platfom/<service>`

### Stage 5: Deploy (5-10 min)
- Creates namespace `vvp` if not exists
- Generates dynamic Helm values with image tags
- Deploys using Helm with 10-minute timeout
- Waits for all pods to be ready

## Troubleshooting

### Common Issues
1. **KUBE_CONFIG_B64 not set**: Pipeline fails at deploy stage
2. **Namespace permissions**: Ensure kubeconfig has cluster-admin or namespace admin rights
3. **Image pull errors**: Verify GitLab Container Registry is enabled
4. **Pod startup failures**: Check resource limits and node capacity

### Debug Commands
```bash
# Check pipeline logs
# Visit: https://gitlab.com/micpward-group/vvp-platfom/-/pipelines

# Check pod logs
kubectl -n vvp logs -f deployment/claims-orchestrator

# Check events
kubectl -n vvp get events --sort-by='.lastTimestamp'

# Check Helm release
helm -n vvp list
helm -n vvp status vvp
```

## Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ claims-         │───▶│ verification-    │───▶│ valuation-      │
│ orchestrator    │    │ service          │    │ service         │
│ (port 8000)     │    │ (port 8000)      │    │ (port 8000)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ payment-        │    │ audit-           │    │ vin-            │
│ service         │    │ service          │    │ monitor         │
│ (port 8000)     │    │ (port 8000)      │    │ (port 8000)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

All services expose:
- `/health` - Health check endpoint
- `/ready` - Readiness probe endpoint
- Service-specific endpoints for business logic

## Expected Timeline
- **MR Creation**: 2 minutes
- **CI/CD Variable Setup**: 1 minute  
- **Pipeline Execution**: 15-20 minutes total
- **Verification**: 5 minutes
- **Total**: ~25-30 minutes from MR to verified deployment
