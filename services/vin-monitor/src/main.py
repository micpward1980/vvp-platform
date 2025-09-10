from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(title="vin-monitor")
WATCH: Dict[str,dict] = {}

class StartReq(BaseModel):
  vin: str
  reason: str
  claimId: str

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

@app.post("/monitor/start")
def start(req: StartReq):
  WATCH[req.vin] = {"reason":req.reason, "claimId":req.claimId}
  return {"status":"watching", "vin": req.vin}

@app.get("/monitor/list")
def listing() -> List[dict]:
  return [{"vin":k, **v} for k,v in WATCH.items()]
