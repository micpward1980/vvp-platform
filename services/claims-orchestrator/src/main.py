from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import os, httpx

SERVICE = os.getenv("SERVICE_NAME","claims-orchestrator")
VERIFY_URL = os.getenv("ORCH_VERIFICATION_URL","http://verification-service:8000")
VALUE_URL  = os.getenv("ORCH_VALUATION_URL","http://valuation-service:8000")
PAY_URL    = os.getenv("ORCH_PAYMENT_URL","http://payment-service:8000")
AUDIT_URL  = os.getenv("ORCH_AUDIT_URL","http://audit-service:8000")
VIN_URL    = os.getenv("ORCH_VIN_URL","http://vin-monitor:8000")

app = FastAPI(title=SERVICE)

class ClaimIn(BaseModel):
    policyId: str
    holderName: str
    vin: str = Field(min_length=11, max_length=32)
    lossDate: datetime
    lossType: str
    details: Optional[str] = None

class Claim(BaseModel):
    claimId: str
    status: str
    policyId: str
    holderName: str
    vin: str
    lossDate: datetime
    lossType: str
    details: Optional[str] = None
    verification: Optional[Dict[str,Any]] = None
    valuation: Optional[Dict[str,Any]] = None
    payment: Optional[Dict[str,Any]] = None
    createdAt: datetime
    updatedAt: datetime

CLAIMS: Dict[str, Claim] = {}

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

@app.get("/") 
def root(): return {"service": SERVICE, "claims": len(CLAIMS)}

async def _audit(event_type:str, data:Dict[str,Any]):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(f"{AUDIT_URL}/audit", json={"eventType":event_type,"data":data})
    except Exception:
        pass

@app.post("/claims", response_model=Claim)
async def file_claim(body: ClaimIn):
    claim_id = str(uuid4())
    now = datetime.utcnow()
    claim = Claim(
        claimId=claim_id, status="FILED",
        policyId=body.policyId, holderName=body.holderName,
        vin=body.vin, lossDate=body.lossDate, lossType=body.lossType,
        details=body.details, createdAt=now, updatedAt=now
    )
    CLAIMS[claim_id] = claim
    await _audit("ClaimFiled", claim.model_dump())
    async with httpx.AsyncClient(timeout=20) as client:
        vreq = {"claimId": claim_id, "policyId": body.policyId, "vin": body.vin,
                "lossType": body.lossType, "lossDate": body.lossDate.isoformat()}
        vres = (await client.post(f"{VERIFY_URL}/verify", json=vreq)).json()
        claim.verification = vres
        claim.status = "VERIFIED" if vres.get("verified") else "ESCALATED"
        claim.updatedAt = datetime.utcnow()
        await _audit("VerificationCompleted", {"claimId":claim_id, **vres})
        print(f"DEBUG ORCHESTRATOR: Verification result for claim {claim_id}: verified={vres.get('verified')}, fraud_score={vres.get('fraudScore')}")
        if not vres.get("verified"):
            print(f"DEBUG ORCHESTRATOR: Claim {claim_id} failed verification - returning without valuation/payment")
            return claim

        valreq = {"claimId": claim_id, "vin": body.vin, "lossType": body.lossType}
        valres = (await client.post(f"{VALUE_URL}/valuate", json=valreq)).json()
        claim.valuation = valres
        claim.status = "VALUATED"
        claim.updatedAt = datetime.utcnow()
        await _audit("ValuationCompleted", {"claimId":claim_id, **valres})

        payout = float(valres.get("payoutAmount",0))
        auto_cap = float(valres.get("autoApproveCap", 7500))
        if payout <= auto_cap:
            payreq = {"claimId": claim_id, "amount": payout, "recipient": body.holderName, "method":"ach"}
            payres = (await client.post(f"{PAY_URL}/pay", json=payreq)).json()
            claim.payment = payres
            if payres.get("status")=="success":
                claim.status = "PAID"
            else:
                claim.status = "APPROVED"
            claim.updatedAt = datetime.utcnow()
            await _audit("PaymentCompleted", {"claimId":claim_id, **payres})
        else:
            claim.status = "APPROVED"  # requires manual release if above cap
            await _audit("ClaimApproved", {"claimId":claim_id, "amount": payout})

        try:
            await client.post(f"{VIN_URL}/monitor/start", json={"vin": body.vin, "reason": body.lossType, "claimId": claim_id})
        except Exception:
            pass

    return claim

@app.get("/claims/{claim_id}", response_model=Claim)
def get_claim(claim_id:str):
    c = CLAIMS.get(claim_id)
    if not c: raise HTTPException(404, "claim not found")
    return c
