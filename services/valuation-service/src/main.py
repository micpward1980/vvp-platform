from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="valuation-service")

BASE_CAP = float(os.getenv("VAL_BASE_CAP","5000"))
BUYUP_CAP = float(os.getenv("VAL_BUYUP_CAP","7500"))
PCT_K = float(os.getenv("VAL_PCT_K","0.10"))  # 10%
AUTO_APPROVE = float(os.getenv("AUTO_APPROVE_CAP","7500"))

class ValReq(BaseModel):
  claimId: str
  vin: str
  lossType: str

class ValRes(BaseModel):
  claimId: str
  preIncidentValue: float
  postIncidentValue: float
  rawDiminishedValue: float
  percentCap: float
  absoluteCap: float
  payoutAmount: float
  autoApproveCap: float

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

@app.post("/valuate", response_model=ValRes)
def valuate(req: ValReq):
  h = sum(ord(c) for c in req.vin) % 10000
  pre = 15000 + (h % 5000)  # 15k–20k
  loss = req.lossType.lower()
  severity_factor = {"hail":0.12,"flood":0.3,"collision":0.22,"theft":0.5,"vandalism":0.08}.get(loss,0.10)
  post = pre * (1 - severity_factor)
  raw = max(0, pre - post)
  pct_cap = pre * PCT_K
  abs_cap = BUYUP_CAP if severity_factor >= 0.2 else BASE_CAP
  payout = min(raw, pct_cap, abs_cap)
  return ValRes(
    claimId=req.claimId, preIncidentValue=round(pre), postIncidentValue=round(post),
    rawDiminishedValue=round(raw), percentCap=round(pct_cap), absoluteCap=round(abs_cap),
    payoutAmount=round(payout), autoApproveCap=round(AUTO_APPROVE)
  )
