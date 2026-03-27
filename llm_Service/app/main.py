from fastapi import FastAPI, Request
from app.api.prompt import questionRouter
from app.api.train import trainRouter
from prometheus_fastapi_instrumentator import Instrumentator
import logging

app = FastAPI()
Instrumentator().instrument(app).expose(app) # Instrumentar el router para Prometheus
app.include_router(questionRouter)
app.include_router(trainRouter)


logger = logging.getLogger("uvicorn") 

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para procesar cada solicitud HTTP."""
    response = await call_next(request)
    
    # Ahora esto funcionará perfecto sin romper el formato
    logger.info(f"Request: {request.method} {request.url} - Response status: {response.status_code}")
    
    return response