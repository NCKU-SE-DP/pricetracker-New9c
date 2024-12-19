from pydantic import BaseModel, Field

MIN_TEXT_LEN = 1
class PromptRequest(BaseModel):
    prompt: str = Field(min_length=MIN_TEXT_LEN)


class NewsSumaryRequestSchema(BaseModel):
    content: str = Field(min_length=MIN_TEXT_LEN)

class NewsSummaryCustomModelRequestSchema(BaseModel):
    content: str = Field(min_length=MIN_TEXT_LEN)
    llm_model: str
