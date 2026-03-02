import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()
API_KEY = os.getenv("API_KEY")

def require_api_key(x_api_key: str | None = Header(default=None)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")