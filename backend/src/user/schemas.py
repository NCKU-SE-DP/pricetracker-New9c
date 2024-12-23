from pydantic import BaseModel, Field

MIN_TEXT_LEN = 1
MAX_TEXT_LEN = 200
class UserAuthSchema(BaseModel):
    username: str = Field(min_length=MIN_TEXT_LEN, max_length=MAX_TEXT_LEN)
    password: str = Field(min_length=MIN_TEXT_LEN, max_length=MAX_TEXT_LEN)
