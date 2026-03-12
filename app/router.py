import time
from groq import Groq
from typing import Optional, Tuple
from app.config import settings


# Configure Groq client
if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "skip_for_now":
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
else:
    groq_client = None


# System prompts for each task type
TASK_PROMPTS = {
    "complete": "You are a helpful AI assistant. Complete the user's request accurately and concisely.",
    "summarize": "You are a summarization expert. Provide a clear, concise summary of the given text. Focus on key points and main ideas.",
    "classify": "You are a text classification expert. Classify the given text into appropriate categories. Respond with the category and a brief explanation.",
    "extract": "You are an information extraction expert. Extract key entities, facts, and structured information from the given text. Present the extracted information in a clear, organized format."
}


def get_system_prompt(task: str, custom_prompt: Optional[str] = None) -> str:
    if custom_prompt:
        return custom_prompt
    return TASK_PROMPTS.get(task, TASK_PROMPTS["complete"])


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    costs = settings.COST_PER_1K_TOKENS.get(model, {"input": 0.001, "output": 0.002})
    input_cost = (input_tokens / 1000) * costs["input"]
    output_cost = (output_tokens / 1000) * costs["output"]
    return round(input_cost + output_cost, 6)


async def call_groq(
    prompt: str,
    system_prompt: str,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> Tuple[str, dict, str]:

    if not groq_client:
        raise Exception("Groq API key not configured")

    response = groq_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    output = response.choices[0].message.content
    tokens = {
        "input": response.usage.prompt_tokens,
        "output": response.usage.completion_tokens,
        "total": response.usage.total_tokens
    }

    return output, tokens, model


# Provider function mapping
PROVIDER_FUNCTIONS = {
    "groq": call_groq
}


def get_default_model(provider: str) -> str:
    return settings.AVAILABLE_MODELS[provider]["default"]


async def route_request(
    task: str,
    input_text: str,
    provider: str = "auto",
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> Tuple[str, dict, str, str, float]:

    sys_prompt = get_system_prompt(task, system_prompt)
    errors = []

    if provider == "auto":
        provider_order = settings.FALLBACK_ORDER
    else:
        provider_order = [provider] + [p for p in settings.FALLBACK_ORDER if p != provider]

    for p in provider_order:
        try:
            call_fn = PROVIDER_FUNCTIONS[p]
            model_to_use = model if model else get_default_model(p)

            start = time.time()
            output, tokens, model_used = await call_fn(
                prompt=input_text,
                system_prompt=sys_prompt,
                model=model_to_use,
                max_tokens=max_tokens,
                temperature=temperature
            )
            latency_ms = (time.time() - start) * 1000

            return output, tokens, p, model_used, latency_ms

        except Exception as e:
            errors.append(f"{p}: {str(e)}")
            continue

    raise Exception(f"All providers failed: {'; '.join(errors)}")
