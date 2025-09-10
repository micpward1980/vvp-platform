from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from dateutil import parser
import httpx
import asyncio
from typing import Optional, List, Dict, Any

app = FastAPI(title="verification-service")

class VerifyReq(BaseModel):
    claimId: str
    policyId: str
    vin: str
    lossType: str
    lossDate: str

class VehicleHistory(BaseModel):
    vin: str
    titleStatus: str
    accidentHistory: List[Dict[str, Any]]
    recallHistory: List[Dict[str, Any]]
    ownershipHistory: List[Dict[str, Any]]
    reportedIncidents: List[Dict[str, Any]]

class VerifyRes(BaseModel):
    claimId: str
    verified: bool
    fraudScore: float
    reasons: list[str]
    requiredHumanReview: bool = False
    vehicleHistory: Optional[VehicleHistory] = None
    policyStatus: str = "ACTIVE"

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

async def lookup_vehicle_history(vin: str) -> Optional[VehicleHistory]:
    """
    Mock VIN lookup service that simulates pulling vehicle history reports.
    In production, this would integrate with Carfax, AutoCheck, or NHTSA APIs.
    """
    try:
        await asyncio.sleep(0.1)
        
        vin_hash = sum(ord(c) for c in vin) % 1000
        print(f"DEBUG: VIN {vin} hash: {vin_hash}, hash%10={vin_hash%10}, hash%15={vin_hash%15}")
        
        if vin.endswith('0'):
            accident_history = [{
                "date": "2024-03-15",
                "type": "Hail Damage",
                "severity": "Moderate",
                "location": "Dallas, TX",
                "repaired": True
            }]
            reported_incidents = [{
                "date": "2024-03-15",
                "type": "Hail Damage",
                "claimNumber": "INS-2024-0315-001",
                "status": "Closed",
                "payoutAmount": 1596.50
            }]
            print(f"DEBUG: VIN {vin} triggered hail damage scenario")
        elif vin.endswith('5'):  # Alternative trigger for flood damage
            accident_history = [{
                "date": "2023-08-20",
                "type": "Flood Damage",
                "severity": "Major",
                "location": "Houston, TX",
                "repaired": True
            }]
            reported_incidents = [{
                "date": "2023-08-20",
                "type": "Flood Damage",
                "claimNumber": "INS-2023-0820-002",
                "status": "Closed",
                "payoutAmount": 4250.00
            }]
            print(f"DEBUG: VIN {vin} triggered flood damage scenario")
        else:
            accident_history = []
            reported_incidents = []
            print(f"DEBUG: VIN {vin} has clean history")
        
        return VehicleHistory(
            vin=vin,
            titleStatus="Clean" if not accident_history else "Rebuilt",
            accidentHistory=accident_history,
            recallHistory=[],
            ownershipHistory=[{
                "owner": "Current Owner",
                "startDate": "2022-01-15",
                "state": "TX"
            }],
            reportedIncidents=reported_incidents
        )
    except Exception as e:
        print(f"VIN lookup failed for {vin}: {e}")
        return None

@app.post("/verify", response_model=VerifyRes)
async def verify(req: VerifyReq):
    reasons = []
    fraud = 0.05
    
    if not req.policyId or not req.policyId[0].isalpha():
        reasons.append("INVALID_POLICY_FORMAT"); fraud += 0.2
    if len(req.vin) < 11:
        reasons.append("SHORT_VIN"); fraud += 0.3
    try:
        dt = parser.isoparse(req.lossDate)
        if dt > datetime.utcnow(): 
            reasons.append("FUTURE_LOSS_DATE"); fraud += 0.4
    except Exception:
        reasons.append("BAD_DATE_FORMAT"); fraud += 0.2
    if req.lossType.lower() not in {"hail","flood","collision","theft","vandalism"}:
        fraud += 0.1
    
    vehicle_history = None
    if len(req.vin) >= 11:
        print(f"DEBUG: Looking up VIN {req.vin}")
        vehicle_history = await lookup_vehicle_history(req.vin)
        print(f"DEBUG: Vehicle history result: {vehicle_history}")
        print(f"DEBUG: Vehicle history type: {type(vehicle_history)}")
        print(f"DEBUG: Vehicle history is None: {vehicle_history is None}")
        print(f"DEBUG: Vehicle history bool: {bool(vehicle_history)}")
        
        if vehicle_history:
            print(f"DEBUG: ENTERING vehicle history check block for VIN {req.vin}")
            print(f"DEBUG: Reported incidents count: {len(vehicle_history.reportedIncidents)}")
            print(f"DEBUG: Reported incidents: {vehicle_history.reportedIncidents}")
            print(f"DEBUG: Reported incidents empty check: {not vehicle_history.reportedIncidents}")
            
            if not vehicle_history.reportedIncidents:
                reasons.append("NO_REPORTED_INCIDENTS")
                fraud += 0.9
                print(f"DEBUG: No reported incidents found for VIN {req.vin} - adding fraud penalty. New fraud score: {fraud}")
            else:
                claim_loss_type = req.lossType.lower()
                claim_date = parser.isoparse(req.lossDate)
                
                matching_incidents = []
                for incident in vehicle_history.reportedIncidents:
                    try:
                        incident_date = parser.isoparse(incident["date"])
                        incident_type = incident["type"].lower()
                        
                        claim_date_naive = claim_date.replace(tzinfo=None) if claim_date.tzinfo else claim_date
                        incident_date_naive = incident_date.replace(tzinfo=None) if incident_date.tzinfo else incident_date
                        
                        if (claim_loss_type in incident_type or incident_type in claim_loss_type):
                            days_diff = abs((claim_date_naive - incident_date_naive).days)
                            if days_diff <= 30:
                                matching_incidents.append(incident)
                    except Exception as e:
                        print(f"DEBUG: Error comparing dates for incident {incident}: {e}")
                        continue
                
                if matching_incidents:
                    reasons.append("DUPLICATE_CLAIM_SUSPECTED")
                    fraud += 0.5
                    print(f"DEBUG: Found matching incidents: {matching_incidents}")
            
            if vehicle_history.titleStatus.lower() in ["salvage", "flood", "lemon"]:
                reasons.append("PROBLEMATIC_TITLE_STATUS")
                fraud += 0.3
        else:
            reasons.append("VIN_LOOKUP_FAILED")
            fraud += 0.1
            print(f"DEBUG: VIN lookup failed for {req.vin}")
    
    verified = fraud < 0.7 and "SHORT_VIN" not in reasons
    policy_status = "ACTIVE"
    
    print(f"DEBUG: Final fraud score: {fraud}, verified: {verified}, reasons: {reasons}")
    print(f"DEBUG: Verification threshold check: fraud ({fraud}) < 0.7 = {fraud < 0.7}")
    print(f"DEBUG: Verification threshold check: fraud ({fraud}) < 0.7 = {fraud < 0.7}")
    
    return VerifyRes(
        claimId=req.claimId, 
        verified=verified, 
        fraudScore=round(min(fraud, 1.0), 3), 
        reasons=reasons, 
        requiredHumanReview=(fraud >= 0.6),
        vehicleHistory=vehicle_history,
        policyStatus=policy_status
    )
