from bcrypt import gensalt, hashpw, checkpw
from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
import uvicorn

class Password(BaseModel):
    password: str = Field(min_length=3, max_length=50)

def hash_password(password: str):
    password_enc = password.encode('utf-8')
    salt = gensalt()
    hashed_password = hashpw(password_enc, salt)
    return hashed_password.decode('utf-8')  

def verify_password(hashed_password: str, input_password: str) -> bool:
    try:
        return checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

app = FastAPI()

@app.post("/create_password")
async def create_password(
    password: Annotated[str, Form(min_length=3, max_length=50)],
    password_check: Annotated[str, Form(min_length=3, max_length=50)]
):
    if password != password_check:
        raise HTTPException(status_code=400, detail="Passwords don't match")
    
    hashed_password = hash_password(password)
    

    if not verify_password(hashed_password, password):
        raise HTTPException(status_code=500, detail="Hashing failed")
    
    return {"message": "Password hashed successfully", "password_hash": hashed_password}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, port=1222)