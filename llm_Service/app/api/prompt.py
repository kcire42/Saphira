from fastapi import APIRouter
from app.LLM_Integration.LLMPrompt import getLLMResponse
from app.api.monitor import LLM_REQUESTS, LLM_ERRORS, LLM_RESPONSE_TIME, LLM_PROMPT_TOKENS, LLM_COMPLETION_TOKENS

questionRouter = APIRouter(prefix='/ask')


@questionRouter.post('/')
async def ask_question(prompt: str):
    LLM_REQUESTS.inc()  # Incrementar el contador de requests
    with LLM_RESPONSE_TIME.time():  # Medir el tiempo de respuesta
        try:
            result = getLLMResponse(prompt)
            answer = result.get("response", "")
            LLM_PROMPT_TOKENS.inc(result["prompt_tokens"])
            LLM_COMPLETION_TOKENS.inc(result["completion_tokens"])

            return {
                "answer": answer,
                "usage": {
                    "prompt_tokens": result["prompt_tokens"],
                    "completion_tokens": result["completion_tokens"]
                }
            }
        except Exception as e:
            LLM_ERRORS.inc()  # Incrementar el contador de errores
            raise e
    