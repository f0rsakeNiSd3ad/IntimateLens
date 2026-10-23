import asyncio
import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import (
    AnalysisRequest, 
    AnalysisResult, 
    HealthResponse, 
    GottmanAnalysis, 
    TimelineEvent, 
    NormalizedMessage
)
from parser import parse_chat_text
from prompt_engine import PromptEngine

app = FastAPI(
    title="IntimacyLens API",
    description="Local-first relationship health analysis web application",
    version="0.1.0"
)

# CORS - configure for frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prompt engine
prompt_engine = PromptEngine()

@app.on_event("startup")
async def startup_event():
    await prompt_engine.initialize()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy",
        gpu_available=gpu_available,
        model_loaded=prompt_engine._initialized and prompt_engine.pipeline is not None,
        model_name=prompt_engine.model_name
    )

def _build_analysis_result(result: dict) -> AnalysisResult:
    """Helper to safely construct an AnalysisResult pydantic model from result dict."""
    toxicity_score = result.get("toxicity_score", 0)
    
    speaker_a = result.get("speaker_a") or "Person A"
    speaker_b = result.get("speaker_b") or "Person B"
    
    normalized_msgs_data = result.get("normalized_conversation", [])
    normalized_msgs = [
        msg if isinstance(msg, NormalizedMessage) else NormalizedMessage(**msg)
        for msg in normalized_msgs_data
        if isinstance(msg, (dict, NormalizedMessage))
    ]
    
    if speaker_a == "Person A" or speaker_b == "Person B":
        discovered = []
        for msg in normalized_msgs:
            sender = msg.original_sender
            if sender and sender not in discovered and sender != "Unknown":
                discovered.append(sender)
        if len(discovered) > 0 and speaker_a == "Person A":
            speaker_a = discovered[0]
        if len(discovered) > 1 and speaker_b == "Person B":
            speaker_b = discovered[1]

    affection_levels = result.get("affection_levels", {})
    person_a_affection = affection_levels.get(speaker_a, affection_levels.get("person_a", 50))
    person_b_affection = affection_levels.get(speaker_b, affection_levels.get("person_b", 50))
    
    key_red_flags = result.get("key_red_flags", [])
    key_green_flags = result.get("key_green_flags", [])
    verdict = result.get("verdict", "Repairable")
    actionable_advice = result.get("actionable_advice", [])
    
    gottman = result.get("gottman_breakdown")
    if gottman and isinstance(gottman, dict):
        gottman_breakdown = GottmanAnalysis(**gottman)
    elif isinstance(gottman, GottmanAnalysis):
        gottman_breakdown = gottman
    else:
        gottman_breakdown = None
    
    timeline_events_data = result.get("timeline_events", [])
    timeline_events = [
        ev if isinstance(ev, TimelineEvent) else TimelineEvent(**ev)
        for ev in timeline_events_data
        if isinstance(ev, (dict, TimelineEvent))
    ]
    
    repair_blueprint = result.get("repair_blueprint")

    return AnalysisResult(
        toxicity_score=int(toxicity_score),
        affection_levels={
            "person_a": int(person_a_affection),
            "person_b": int(person_b_affection),
            speaker_a: int(person_a_affection),
            speaker_b: int(person_b_affection)
        },
        key_red_flags=key_red_flags,
        key_green_flags=key_green_flags,
        verdict=verdict,
        actionable_advice=actionable_advice,
        gottman_breakdown=gottman_breakdown,
        timeline_events=timeline_events,
        normalized_conversation=normalized_msgs,
        repair_blueprint=repair_blueprint,
        speaker_a=speaker_a,
        speaker_b=speaker_b
    )

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_chat(
    file: UploadFile = File(...),
    user_instructions: str = Form("")
):
    """
    Analyze an uploaded chat export file.
    Supports .txt and .json formats (WhatsApp, Instagram, SMS).
    """
    # Validate file type
    filename = (file.filename or "").lower()
    if not (filename.endswith('.txt') or filename.endswith('.json')):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload .txt or .json files."
        )
    
    # Read file content with robust decoding
    try:
        content = await file.read()
        try:
            content_str = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                content_str = content.decode('latin-1')
            except Exception:
                content_str = content.decode('utf-8', errors='replace')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Parse chat messages
    messages = parse_chat_text(content_str)
    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in the chat export. Please check the file format.")
    
    # Run analysis pipeline
    try:
        result = await prompt_engine.run_full_analysis(messages, user_instructions)
        if not result:
            raise HTTPException(status_code=500, detail="Analysis failed. The engine returned unexpected output.")
        
        return _build_analysis_result(result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/analyze/json", response_model=AnalysisResult)
async def analyze_chat_json(req: AnalysisRequest):
    """Direct JSON endpoint to analyze plain text without multipart file upload."""
    if not req.chat_text or not req.chat_text.strip():
        raise HTTPException(status_code=400, detail="chat_text is required.")
    
    messages = parse_chat_text(req.chat_text)
    if not messages:
        raise HTTPException(status_code=400, detail="No messages found in chat_text.")
    
    result = await prompt_engine.run_full_analysis(messages, req.user_instructions or "")
    if not result:
        raise HTTPException(status_code=500, detail="Analysis failed.")
    
    return _build_analysis_result(result)

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)