import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    AVAILABLE_MODELS = {
        "groq": {
            "provider": "groq",
            "models": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "default": "llama-3.3-70b-versatile"
        }
    }
    
    FALLBACK_ORDER = ["groq"]
    
    COST_PER_1K_TOKENS = {
        "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
        "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
        "mixtral-8x7b-32768": {"input": 0.00024, "output": 0.00024},
        "gemma2-9b-it": {"input": 0.00020, "output": 0.00020}
    }

settings = Settings()
