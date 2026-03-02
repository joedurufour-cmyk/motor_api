from typing import Dict, Any

def run_motor(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if name == "echo":
        return {"echo": payload}
    raise ValueError("Motor not found")