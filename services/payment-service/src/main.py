from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict

app = FastAPI(title="payment-service")
PAID: Dict[str,bool] = {}

class PayReq(BaseModel):
  claimId: str
  amount: float
  recipient: str
  method: str = "ach"

class PayRes(BaseModel):
  status: str
  transactionId: str
  method: str
  amount: float

@app.get("/health") 
def health(): return {"status":"ok"}

@app.get("/ready") 
def ready(): return {"status":"ok"}

@app.post("/pay", response_model=PayRes)
def pay(req: PayReq):
  if PAID.get(req.claimId):
    tid = f"dup-{req.claimId[:8]}"
    return PayRes(status="success", transactionId=tid, method=req.method, amount=req.amount)
  tid = str(uuid4())
  PAID[req.claimId] = True
  return PayRes(status="success", transactionId=tid, method=req.method, amount=req.amount)
