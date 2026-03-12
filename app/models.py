from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class TaskType(str, Enum):
    COMPLETE = "complete"
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"
    EXTRACT = "extract"


class Provider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AUTO = "auto"


class AIRequest(BaseModel):
    task: TaskType = Field(..., description="Type of AI task")
    input_text: str = Field(..., description="Input text to process")
    provider: Provider = Field(default=Provider.AUTO, description="LLM provider")
    model: Optional[str] = Field(default=None, description="Specific model name")
    max_tokens: int = Field(default=1000, description="Maximum output tokens")
    temperature: float = Field(default=0.7, description="Creativity level 0-1")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "summarize",
                "input_text": "Artificial intelligence is transforming how we work...",
                "provider": "groq",
                "max_tokens": 500,
                "temperature": 0.5
            }
        }


class AIResponse(BaseModel):
    success: bool
    task: str
    provider: str
    model: str
    output: str
    tokens_used: dict
    cost_usd: float
    latency_ms: float
    cached: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    provider_tried: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class HealthResponse(BaseModel):
    status: str
    providers: dict
    total_requests: int
    uptime: str


class MetricsResponse(BaseModel):
    total_requests: int
    total_cost_usd: float
    average_latency_ms: float
    requests_by_provider: dict
    requests_by_task: dict
    error_rate: float
    cache_hit_rate: float
