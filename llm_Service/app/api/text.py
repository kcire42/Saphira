from fastapi import APIRouter
from app.LLM_Integration.LLMPrompt import getLLMtextSummary
from app.api.monitor import LLM_REQUESTS, LLM_ERRORS, LLM_RESPONSE_TIME, LLM_PROMPT_TOKENS, LLM_COMPLETION_TOKENS
from app.api.baseModel import TextRequest

textRouter = APIRouter(prefix='/text')


@textRouter.post('/')
async def summarize_text(request: TextRequest):
    LLM_REQUESTS.inc()  # Incrementar el contador de requests
    with LLM_RESPONSE_TIME.time():  # Medir el tiempo de respuesta
        try:
            result = getLLMtextSummary(request.text, llmResource=request.llm_resource)  # Cambia a True para usar el LLM en la nube
            print(f"✅ Resultado del LLM: {result}")
            answer = result.get("response", "")
            LLM_PROMPT_TOKENS.inc(result["prompt_tokens"])
            LLM_COMPLETION_TOKENS.inc(result["completion_tokens"])

            return {
                "response": answer,
                "usage": {
                    "prompt_tokens": result["prompt_tokens"],
                    "completion_tokens": result["completion_tokens"]
                }
            }
        except Exception as e:
            LLM_ERRORS.inc()  # Incrementar el contador de errores
            raise e