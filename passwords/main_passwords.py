from fastapi import APIRouter,Depends,Form,HTTPException,Body
from schemas import Password
from models import init_db,Session
from typing import Annotated
from hash_functions import verify_password,hash_password

router = APIRouter()

@router.post("/create_password")
async def create_password(
    password: Password,
    password_check: Password,
    db: Session = Depends(init_db)
):
    if password != password_check:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    hashed_password = hash_password(password)

    if verify_password(hashed_password,password_check) == False:
        raise HTTPException(status_code=500,detail="Hash did not work")
    
    db.add(hashed_password)
    db.commit()
    db.refresh(hashed_password)

    return password

@router.delete("/delete_password")
async def delete_password(
    password: Password,
    db:Session = Depends(init_db)
):
    db.delete(password)
    db.commit()
    return {"status":"password deleted"}

@router.get("/get_password")
async def get_passwords(
    db: Session = Depends(init_db)
):
    passwords = db.query(Password).all()
    return passwords