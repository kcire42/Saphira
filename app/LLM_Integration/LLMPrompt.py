import requests
from .config import OLLAMA_API_URL, MODEL_NAME , REQUEST_TIMEOUT_SECONDS
from app.LLMGetInfo.doc.getLLMContext import getdocContext

def getLLMResponse(prompt: str) -> str:
    answer = routeAnswerToLLM(prompt)
    return answer

def routeQuestionToLLM(prompt: str) -> str:
    ROUTER_PROMPT = """
    Eres el clasificador de intención de un asistente personal inteligente.
    Tu trabajo es dirigir la duda del usuario a la fuente de datos correcta.
    
    DEFINICIONES:
    - RAG_ONLY: Consultas sobre mis notas, reflexiones, resúmenes de libros, guías que he guardado o "cómo hacer algo" según mis propios documentos.
    - SQL_ONLY: Consultas de datos numéricos o registros específicos en mi base de datos (ej: "cuánto gasté", "cuántos pasos di", "a qué hora me dormí", "cuánta agua tomé").
    - HYBRID: Cuando pido un análisis que cruza mis notas con mis datos (ej: "¿Cómo afectó mi café de la tarde a mi sueño de anoche?").
    
    Pregunta del Usuario:
    {prompt}
    
    REGLAS DE SALIDA:
    - Responde ÚNICAMENTE con una de las tres palabras: RAG_ONLY, SQL_ONLY, o HYBRID.
    - Sin puntos ni explicaciones.
    """
    response = callLLM(ROUTER_PROMPT.format(prompt=prompt))
    return response

def routeAnswerToLLM(prompt: str) -> str:
    route = routeQuestionToLLM(prompt)
    if route == "RAG_ONLY":
        return ragAnswerToLLM(prompt)
    elif route == "SQL_ONLY":
        return sqlAnswerToLLM(prompt)
    elif route == "HYBRID":
        return hybridAnswerToLLM(prompt)
    raise ValueError(f"Unknown route: {route}")


def ragAnswerToLLM(prompt: str) -> str:
    docContext = getdocContext(prompt)
    RAGPrompt = f"""
    Eres mi asistente personal y mentor. Tu tono es cálido, alentador y organizado.
        
    MEMORIA DISPONIBLE (Mis notas y documentos):
    {docContext}
    
    PREGUNTA:
    {prompt}
    
    INSTRUCCIONES:
    1. Responde basándote en mis notas de forma natural (ej: "En tus notas sobre X, mencionaste...").
    2. Si explicas un proceso personal, usa pasos numerados claros.
    3. Si menciono una meta o hábito en el texto, recuérdamelo con entusiasmo.
    
    Formato de respuesta:
    **Enfoque** → Breve resumen
    **Pasos sugeridos / Recordatorios:**
    1. Punto uno
    2. Punto dos...
    """
    return callLLM(RAGPrompt)

def sqlAnswerToLLM(prompt: str) -> str:
    sqlResults = "Sample SQL data results relevant to the question."
    SQLPrompt = f"""
    Eres mi analista de datos personales. 
    Reglas:
    - Sé directo pero amable. 
    - No inventes números que no estén en los datos.
    - Si ves algo inusual (ej: gasté mucho hoy), coméntalo como un amigo preocupado pero profesional.

    Datos registrados:
    {sqlResults}

    Pregunta:
    {prompt}
    """
    return callLLM(SQLPrompt)

def hybridAnswerToLLM(prompt: str) -> str:
    docContext = getdocContext(prompt)
    sqlResults = "Sample SQL data results relevant to the question."
    hybridPrompt = f"""
    Eres mi Coach de Vida. Tu objetivo es conectar lo que siento (notas) con lo que hago (datos).
    
    Contexto Vital (Notas):
    {docContext}

    Métricas (Datos):
    {sqlResults}

    Instrucciones:
    - Analiza si mis métricas coinciden con mis intenciones o estados de ánimo en las notas.
    - Ofrece un consejo práctico y humano basado en esta conexión.
    - Tono: Empático y motivador.

    Pregunta del usuario:
    {prompt}
    """
    return callLLM(hybridPrompt)


def callLLM(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 250
        }
    }

    response = requests.post(OLLAMA_API_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    answer = response.json()["response"]
    return answer
