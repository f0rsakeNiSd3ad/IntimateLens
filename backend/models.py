from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    timestamp: Optional[str] = None
    sender: str
    message: str

class NormalizedMessage(BaseModel):
    original_sender: str
    normalized_text: str
    original_text: str
    emotion_tone: Optional[str] = None

class TimelineEvent(BaseModel):
    timestamp: Optional[str] = "N/A"
    speaker: str
    message: Optional[str] = ""
    sentiment_impact: int = Field(description="Impact score from -100 (highly toxic) to +100 (highly affectionate)")
    label: str = Field(description="Short classification, e.g., 'Contempt Spike', 'Bids for Connection', 'Defensiveness'")

class GottmanAnalysis(BaseModel):
    criticism_score: int = Field(default=0, ge=0, le=100)
    contempt_score: int = Field(default=0, ge=0, le=100)
    defensiveness_score: int = Field(default=0, ge=0, le=100)
    stonewalling_score: int = Field(default=0, ge=0, le=100)
    notes: Optional[str] = ""

class AnalysisResult(BaseModel):
    toxicity_score: int = Field(ge=0, le=100, description="Overall relationship toxicity score from 0 to 100")
    affection_levels: Dict[str, int] = Field(description="Affection level per person (0 to 100)")
    key_red_flags: List[str] = Field(default_factory=list)
    key_green_flags: List[str] = Field(default_factory=list)
    verdict: str = Field(description="Verdict: 'Healthy', 'Repairable', 'Critical', or 'Recommend Ending'")
    actionable_advice: List[str] = Field(default_factory=list)
    gottman_breakdown: Optional[GottmanAnalysis] = None
    timeline_events: List[TimelineEvent] = Field(default_factory=list)
    normalized_conversation: List[NormalizedMessage] = Field(default_factory=list)
    repair_blueprint: Optional[Dict[str, Any]] = None
    speaker_a: Optional[str] = Field(default="Person A", description="Identified name of first participant")
    speaker_b: Optional[str] = Field(default="Person B", description="Identified name of second participant")

class AnalysisRequest(BaseModel):
    chat_text: Optional[str] = None
    user_instructions: Optional[str] = Field(default="", description="User provided context, e.g. Hinglish, slang, relationship context")
    model_name: Optional[str] = Field(default="Qwen/Qwen2.5-7B-Instruct")

class HealthResponse(BaseModel):
    status: str
    gpu_available: bool
    model_loaded: bool
    model_name: str
