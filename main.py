from fastapi import FastAPI, Form, HTTPException
from typing import Annotated
import uvicorn
from hash_functions import hash_password,verify_password


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