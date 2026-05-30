from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Ensure the original logic can be imported or directly accessed
# For now, I'll copy the core logic into a service file within the backend
from backend.humanizer_service import recursive_humanize

app = FastAPI()

class HumanizeRequest(BaseModel):
    text: str
    iterations: int = 8
    intensity: str = "standard"

@app.post("/api/humanize")
async def humanize(request: HumanizeRequest):
    final_text, analysis = recursive_humanize(request.text, request.iterations, request.intensity)
    return {"text": final_text, "analysis": analysis}
