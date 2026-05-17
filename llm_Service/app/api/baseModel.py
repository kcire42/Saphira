from pydantic import BaseModel



class QuestionModel(BaseModel):
    user : str
    question : str

class TextRequest(BaseModel):
    text: str
    llm_resource: bool = False  

