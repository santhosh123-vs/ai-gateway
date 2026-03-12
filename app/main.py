import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    AIRequest, AIResponse, ErrorResponse,
    HealthResponse, MetricsResponse
)
from app.router import route_request, calculate_cost, PROVIDER_FUNCTIONS
from app.cache import cache
from app.monitor import monitor
from app.config import settings


app = FastAPI(
    title="AI Gateway — Unified LLM API",
    description="""
    A unified REST API that abstracts multiple AI providers 
    behind a single interface.
    
    Features:
    - Smart model routing with automatic fallback
    - Response caching to reduce costs
    - Real-time monitoring and cost tracking
    - Multiple AI tasks: complete, summarize, classify, extract
    
    Built by [YOUR NAME] as an AI Platform Infrastructure project.
    """,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
async def home():
    return {
        "name": "AI Gateway — Unified LLM API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/v1/complete": "General AI completion",
            "POST /api/v1/summarize": "Summarize text",
            "POST /api/v1/classify": "Classify text",
            "POST /api/v1/extract": "Extract information",
            "GET /api/v1/health": "Check provider status",
            "GET /api/v1/metrics": "View usage metrics",
            "GET /api/v1/models": "List available models",
            "GET /api/v1/logs": "Recent request logs"
        },
        "docs": "/docs"
    }


async def process_request(request: AIRequest, task_override: str = None):
    task = task_override or request.task.value
    provider = request.provider.value
    model = request.model

    cache_model = model or "default"
    cached_response = cache.get(task, request.input_text, cache_model, request.temperature)

    if cached_response:
        monitor.log_request(
            task=task,
            provider=cached_response["provider"],
            model=cached_response["model"],
            latency_ms=0,
            tokens_used=cached_response["tokens_used"],
            cost_usd=0,
            success=True,
            cached=True
        )
        return AIResponse(
            success=True,
            task=task,
            provider=cached_response["provider"],
            model=cached_response["model"],
            output=cached_response["output"],
            tokens_used=cached_response["tokens_used"],
            cost_usd=0,
            latency_ms=0,
            cached=True
        )

    try:
        output, tokens, provider_used, model_used, latency_ms = await route_request(
            task=task,
            input_text=request.input_text,
            provider=provider,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt
        )

        cost = calculate_cost(model_used, tokens["input"], tokens["output"])

        monitor.log_request(
            task=task,
            provider=provider_used,
            model=model_used,
            latency_ms=latency_ms,
            tokens_used=tokens,
            cost_usd=cost,
            success=True
        )

        cache.set(task, request.input_text, cache_model, request.temperature, {
            "output": output,
            "provider": provider_used,
            "model": model_used,
            "tokens_used": tokens
        })

        return AIResponse(
            success=True,
            task=task,
            provider=provider_used,
            model=model_used,
            output=output,
            tokens_used=tokens,
            cost_usd=cost,
            latency_ms=round(latency_ms, 2)
        )

    except Exception as e:
        monitor.log_request(
            task=task,
            provider=provider,
            model=model or "unknown",
            latency_ms=0,
            tokens_used={},
            cost_usd=0,
            success=False
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/complete", response_model=AIResponse, tags=["AI Tasks"])
async def complete(request: AIRequest):
    """General AI completion"""
    return await process_request(request, task_override="complete")


@app.post("/api/v1/summarize", response_model=AIResponse, tags=["AI Tasks"])
async def summarize(request: AIRequest):
    """Summarize the given text"""
    return await process_request(request, task_override="summarize")


@app.post("/api/v1/classify", response_model=AIResponse, tags=["AI Tasks"])
async def classify(request: AIRequest):
    """Classify the given text"""
    return await process_request(request, task_override="classify")


@app.post("/api/v1/extract", response_model=AIResponse, tags=["AI Tasks"])
async def extract(request: AIRequest):
    """Extract key information from text"""
    return await process_request(request, task_override="extract")


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Monitoring"])
async def health():
    """Check which AI providers are available"""
    providers = {}
    
    providers["groq"] = "active" if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "skip_for_now" else "not configured"
    providers["google"] = "active" if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "skip_for_now" else "not configured"
    providers["openai"] = "active" if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "skip_for_now" else "not configured"
    providers["anthropic"] = "active" if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "skip_for_now" else "not configured"

    metrics = monitor.get_metrics()

    return HealthResponse(
        status="healthy",
        providers=providers,
        total_requests=metrics["total_requests"],
        uptime=metrics["uptime"]
    )


@app.get("/api/v1/metrics", tags=["Monitoring"])
async def metrics():
    """Get detailed usage metrics"""
    data = monitor.get_metrics()
    data["cache_stats"] = cache.get_stats()
    return data


@app.get("/api/v1/logs", tags=["Monitoring"])
async def logs(limit: int = 20):
    """Get recent request logs"""
    return {
        "recent_requests": monitor.get_recent_requests(limit),
        "total_requests": monitor.total_requests
    }


@app.get("/api/v1/models", tags=["Info"])
async def list_models():
    """List all available AI models"""
    return {
        "providers": settings.AVAILABLE_MODELS,
        "fallback_order": settings.FALLBACK_ORDER,
        "cost_per_1k_tokens": settings.COST_PER_1K_TOKENS
    }


@app.get("/api/v1/cache/stats", tags=["Monitoring"])
async def cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


@app.delete("/api/v1/cache/clear", tags=["Monitoring"])
async def clear_cache():
    """Clear all cached responses"""
    cache.clear()
    return {"message": "Cache cleared successfully"}
