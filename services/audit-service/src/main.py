from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(title="audit-service")
LOGS: List[Dict[str,Any]] = []

class AuditIn(BaseModel):
  eventType: str
  data: Dict[str,Any]

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

@app.post("/audit")
def audit(body: AuditIn):
  LOGS.append({"ts": datetime.utcnow().isoformat(), **body.model_dump()})
  return {"status":"logged"}

@app.get("/audit/claim/{claim_id}")
def by_claim(claim_id:str):
  return [l for l in LOGS if l.get("data",{}).get("claimId")==claim_id]

@app.get("/audit")
def all_logs():
  return LOGS[-200:]
