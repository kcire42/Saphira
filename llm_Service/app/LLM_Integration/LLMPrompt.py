from app.LLM_Integration.Call_LLM import selectLLM


def getLLMResponse(prompt: str,llmResource: bool = False) -> dict:
    answer = routeAnswerToLLM(prompt, llmResource=llmResource)
    return answer


def routeQuestionToLLM(prompt: str,llmResource: bool = False) -> dict:
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
    response = selectLLM(ROUTER_PROMPT.format(prompt=prompt), llmResource=llmResource)
    print(f"LLM Router Response: {response}")
    return response
    


def routeAnswerToLLM(prompt: str, llmResource: bool = False) -> dict:
    data = routeQuestionToLLM(prompt, llmResource=llmResource)
    print(f"Routing decision: {data}")
    route = data.get("text", "").strip()
    if route == "RAG_ONLY":
        return ragAnswerToLLM(prompt, llmResource=llmResource)
    elif route == "SQL_ONLY":
        return sqlAnswerToLLM(prompt, llmResource=llmResource)
    elif route == "HYBRID":
        return hybridAnswerToLLM(prompt, llmResource=llmResource)
    raise ValueError(f"Unknown route: {route}")


def ragAnswerToLLM(prompt: str, llmResource: bool = False) -> dict:
    docContext = ''#getdocContext(prompt)
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
    response = selectLLM(RAGPrompt.format(prompt=prompt), llmResource=llmResource)
    return response

def sqlAnswerToLLM(prompt: str, llmResource: bool = False) -> dict:
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
    response = selectLLM(SQLPrompt.format(prompt=prompt), llmResource=llmResource)
    return response

def hybridAnswerToLLM(prompt: str, llmResource: bool = False) -> dict:
    docContext = ''#getdocContext(prompt)
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
    response = selectLLM(hybridPrompt.format(prompt=prompt), llmResource=llmResource)
    return response


def getLLMtextSummary(text: str, llmResource: bool = False) -> dict:
    summaryPrompt = f"""
    Eres un asistente de resumen de texto. Tu tarea es condensar el siguiente texto en un resumen claro y conciso, destacando los puntos clave y eliminando información redundante.

    Texto a resumir:
    {text}

    Instrucciones:
    - Crea un resumen que capture la esencia del texto.
    - Mantén la coherencia y el flujo natural.
    - Evita incluir detalles menores o ejemplos específicos a menos que sean cruciales para la comprensión general.

    Resumen:
    """
    response = selectLLM(summaryPrompt.format(text=text), llmResource=llmResource)
    return response


