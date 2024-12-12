from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str


class NewsSumaryRequestSchema(BaseModel):
    content: str

class NewsSummaryCustomModelRequestSchema(BaseModel):
    content: str
    llm_model: str
