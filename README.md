# VVP Platform - Ready to Deploy

This is a single-container version of the VVP Platform that works on Railway, Render, and other hosting platforms.

## Quick Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Upload this folder or connect to your GitHub repo
5. Railway will automatically detect the Dockerfile and deploy

## What's Included

- All 6 microservices (claims-orchestrator, verification-service, valuation-service, payment-service, vin-monitor, audit-service)
- Web UI served by nginx
- Single Dockerfile that runs everything with supervisor
- All services communicate via localhost ports

## Testing

Once deployed, test with these VINs:
- VIN ending in "1": Clean history → ESCALATED status, $0 payout
- VIN ending in "0": Hail damage → PAID status, with payout amount

The platform will be available on port 3000 of your deployed URL.
