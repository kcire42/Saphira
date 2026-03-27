from fastapi import APIRouter
from prometheus_client import Counter, Histogram



# Número de requests al LLM
LLM_REQUESTS = Counter(
    "llm_requests_total",
    "Total requests  LLM"
)

# Errores
LLM_ERRORS = Counter(
    "llm_errors_total",
    "Errors LLM"
)

# Tiempo de respuesta
LLM_RESPONSE_TIME = Histogram(
    "llm_response_seconds",
    "Response time LLM"
)

# Tokens usados en prompts y respuestas
LLM_PROMPT_TOKENS = Counter(
    "llm_prompt_tokens_total",
    "Total prompt tokens"
)

LLM_COMPLETION_TOKENS = Counter(
    "llm_completion_tokens_total",
    "Total completion tokens"
)
