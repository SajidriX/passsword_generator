from pydantic import BaseModel,Field

class SPassword(BaseModel):
    password: str = Field(min_length=8,max_length=128)
    service: str = Field(min_length=3,max_length=500)
    description: str = Field(min_length=3,max_length=500)