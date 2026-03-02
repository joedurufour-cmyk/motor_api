import time
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .auth import require_api_key
from .motors import run_motor

app = FastAPI(title="Motor API (Local)", version="1.0.0")

class RunRequest(BaseModel):
    input: Dict[str, Any]

@app.get("/v1/health")
def health():
    return {"ok": True, "ts": int(time.time())}

@app.post("/v1/motors/{motor_name}/run")
def execute_motor(motor_name: str, request: RunRequest, _=Depends(require_api_key)):
    try:
        result = run_motor(motor_name, request.input)
        return {"ok": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))