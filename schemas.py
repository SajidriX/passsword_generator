from pydantic import BaseModel,Field

class Password(BaseModel):
    password: str = Field(min_length=3,max_length=500)