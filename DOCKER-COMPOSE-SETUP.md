# VVP Platform - Docker Compose Deployment

## Quick Start (5 minutes)

Since EKS cluster creation is having issues, let's get the VVP platform running locally with Docker Compose:

### Prerequisites
- Docker and Docker Compose installed
- All VVP platform code (already ready in this directory)

### 1. Build and Start All Services
```bash
cd /path/to/vvp-platform
docker-compose up --build
```

This will:
- Build Docker images for all 6 microservices
- Start all services with proper networking
- Expose claims-orchestrator on port 8000

### 2. Test the Platform
Once all services are running (takes ~2-3 minutes), test the claims workflow:

```bash
# Submit a test claim
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

Expected response: JSON with claimId and status "PAID"

### 3. Check Audit Logs
```bash
# Get last 5 audit entries
curl http://localhost:8000/audit | jq '.[-5:]'
```

### 4. View Service Health
```bash
# Check all service health endpoints
curl http://localhost:8000/health  # claims-orchestrator
curl http://localhost:8001/health  # verification-service (if exposed)
```

## Service Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ claims-         │───▶│ verification-    │───▶│ valuation-      │
│ orchestrator    │    │ service          │    │ service         │
│ (port 8000)     │    │ (internal)       │    │ (internal)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ payment-        │    │ audit-           │    │ vin-            │
│ service         │    │ service          │    │ monitor         │
│ (internal)      │    │ (internal)       │    │ (internal)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Advantages of Docker Compose
- ✅ **Fast setup**: 5 minutes vs 60+ minutes for EKS
- ✅ **No cloud costs**: Runs locally
- ✅ **Easy debugging**: Direct access to logs
- ✅ **Complete workflow**: All 6 services working together
- ✅ **Immediate testing**: Can test claims API right away

## Commands
```bash
# Start services
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f claims-orchestrator

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build verification-service
docker-compose up -d verification-service
```

## Next Steps
Once Docker Compose is working:
1. Demonstrate the complete claims workflow
2. Show audit logging functionality
3. Verify all 6 microservices are communicating
4. Can still work on EKS deployment in parallel

This gives you a fully functional VVP platform immediately while we troubleshoot the EKS cluster issues!
