# VVP Platform Web UI Setup

## Overview
The VVP platform now includes a professional web UI for client demonstrations. The UI provides a complete interface for submitting claims and viewing the automated processing results across all 6 microservices.

## Quick Start

### 1. Start the Complete Platform
```bash
cd vvp-platform
docker-compose up -d --build
```

This will start:
- All 6 VVP microservices (claims-orchestrator, verification, valuation, payment, vin-monitor, audit)
- Web UI on port 3000

### 2. Access the Demo UI
Open your browser and go to: **http://localhost:3000**

### 3. Demo the Claims Workflow
1. Fill out the claim form with sample data (pre-populated)
2. Click "Submit Claim" 
3. Watch the real-time processing across all microservices
4. View detailed results including:
   - Verification status and fraud score
   - Valuation amount and damage assessment
   - Payment processing and transaction ID
   - Complete audit trail

## Features

### Professional UI
- Modern, responsive design
- Real-time claim processing
- Status indicators and progress tracking
- Detailed results display

### Complete Workflow Demo
- **Claim Submission**: Policy holder information and incident details
- **Verification Service**: Fraud detection and policy validation
- **Valuation Service**: Damage assessment and payout calculation
- **Payment Service**: Automated payment processing
- **VIN Monitor**: Vehicle tracking and watchlist management
- **Audit Service**: Complete event logging and compliance

### Client-Ready Features
- Professional branding and styling
- Clear status indicators (PAID, APPROVED, ESCALATED)
- Detailed breakdown of processing steps
- Error handling and user feedback
- Mobile-responsive design

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Web UI          │───▶│ Nginx Proxy      │───▶│ Claims          │
│ (Port 3000)     │    │ (/api/* → :8000) │    │ Orchestrator    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │ 5 Microservices │
                                               │ (Internal)      │
                                               └─────────────────┘
```

## Sample Demo Flow

1. **Open UI**: Navigate to http://localhost:3000
2. **Submit Claim**: Use pre-filled sample data or customize
3. **Watch Processing**: Real-time updates as claim flows through services
4. **View Results**: Complete breakdown of verification, valuation, and payment
5. **Show Audit Trail**: Demonstrate compliance and logging capabilities

## Customization

### Sample Data
The form comes pre-populated with realistic sample data:
- Policy ID: P-1001
- Holder: Alex Driver
- VIN: 1HGCM82633A004352
- Loss Type: Hail Damage

### Styling
The UI uses a professional blue gradient theme with:
- Modern card-based layout
- Status indicators with color coding
- Responsive design for all screen sizes
- Professional typography and spacing

## Troubleshooting

### UI Not Loading
- Ensure Docker Compose is running: `docker-compose ps`
- Check port 3000 is not in use by another application
- Verify nginx container is healthy: `docker-compose logs web-ui`

### API Errors
- Check claims-orchestrator is running: `curl http://localhost:8000/health`
- View service logs: `docker-compose logs claims-orchestrator`
- Ensure all 6 microservices are healthy: `docker-compose ps`

### CORS Issues
- The nginx configuration handles CORS automatically
- If issues persist, check nginx.conf configuration
- Restart containers: `docker-compose restart web-ui`

## Commands

```bash
# Start all services including UI
docker-compose up -d --build

# View UI logs
docker-compose logs -f web-ui

# View API logs
docker-compose logs -f claims-orchestrator

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose up -d --build
```

## Client Demo Script

1. **Introduction**: "This is the VVP platform - a complete vehicle verification and payment system"
2. **Show Form**: "Here's how a claim is submitted with policy and incident details"
3. **Submit Claim**: "Watch as the claim flows through our 6 microservices automatically"
4. **Explain Results**: "The system verified the claim, calculated the payout, and processed payment - all in seconds"
5. **Highlight Features**: "Notice the fraud detection, automated valuation, and instant payment processing"

The UI is now ready for professional client demonstrations!
