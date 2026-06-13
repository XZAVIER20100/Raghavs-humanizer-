from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
import traceback

# Ensure the original logic can be imported or directly accessed
from backend.humanizer_service import recursive_humanize

app = FastAPI()

class HumanizeRequest(BaseModel):
    text: str
    iterations: int = 5
    intensity: str = "standard"

@app.post("/api/humanize")
async def humanize(request: HumanizeRequest):
    try:
        if not request.text.strip():
            return {"text": "", "analysis": "Empty input provided."}
            
        final_text, analysis = recursive_humanize(request.text, request.iterations, request.intensity)
        return {"text": final_text, "analysis": analysis}
    except Exception as e:
        print(f"Error during humanization: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
