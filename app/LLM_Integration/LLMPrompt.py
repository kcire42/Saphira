import requests
from .config import OLLAMA_API_URL, MODEL_NAME , REQUEST_TIMEOUT_SECONDS
from app.LLMGetInfo.doc.getLLMContext import getdocContext

def getLLMResponse(prompt: str) -> str:
    answer = routeAnswerToLLM(prompt)
    return answer

def routeQuestionToLLM(prompt: str) -> str:
    ROUTER_PROMPT = """
    You are an intelligent intent classifier for an Industrial SCADA system.
    
    Your job is to route the user's question to the correct data source.
    
    DEFINITIONS:
    - RAG_ONLY: Use this for questions about "How to configure", "How to create", "Steps", "Definitions", "Manuals", "GUI navigation", or "Ignition Designer".
    - SQL_ONLY: Use this ONLY for questions asking for specific numerical values from the database (e.g., "What is the temperature?", "How many alarms?", "Show me the last 5 values").
    - HYBRID: Use this when the user asks for a value AND an explanation of what it means contextually.
    
    User Question:
    {prompt}
    
    OUTPUT RULES:
    - Respond ONLY with one of the three words: RAG_ONLY, SQL_ONLY, or HYBRID.
    - Do not add punctuation or explanation.
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
    You are an expert technical consultant for this Ignition project.
        
        SOURCE MATERIAL:
        {docContext}
        
        USER QUESTION:
        {prompt}
        
        INSTRUCTIONS:
        1. Base your answer PRIMARILY on the "SOURCE MATERIAL".
        2. INTERPRETATION ALLOWED: If the text describes a process in a sentence (e.g., "Right click folder and select X"), convert it into clear numbered steps.
        3. LOOK FOR: Specific keywords like "New Tag", "Data Type Instance", "UDT", or specific folder names mentioned in the text.
        4. PROPERTIES: List specific tag parameters mentioned (like _ResourceID, FailedPartCount) if present.
        5. If the text mentions a specific example (like "Rezum line" or "Arden Hills"), use it as an example.
        
        Format your answer as:
        **Concept** → Explanation
        **Configuration Steps:**
        1. Step one
        2. Step two...
        
        Answer:
                """
    return callLLM(RAGPrompt)

def sqlAnswerToLLM(prompt: str) -> str:
    sqlResults = "Sample SQL data results relevant to the question."
    SQLPrompt = f"""
    You are an industrial data analyst.
    Rules:
    - Use ONLY the provided data
    - Do NOT assume missing values
    - Identify anomalies
    - Suggest corrective actions
    - Be concise and technical

    Measured data:
    {sqlResults}

    User question:
    {prompt}
    """
    return callLLM(SQLPrompt)

def hybridAnswerToLLM(prompt: str) -> str:
    docContext = getdocContext(prompt)
    sqlResults = "Sample SQL data results relevant to the question."
    hybridPrompt = f"""
    You are an industrial data analyst.
    Rules:
    - Use ONLY the provided data
    - Do NOT assume missing values
    - Identify anomalies
    - Suggest corrective actions
    - Be concise and technical

    Operational documentation:
    {docContext}

    Measured data:
    {sqlResults}

    User question:
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
