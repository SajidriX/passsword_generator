from fastapi import APIRouter,Depends,Form,HTTPException,Body,Request
from models import init_db,Session,Password
from typing import Annotated
from hash_functions import verify_password,hash_password
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas import SPassword



router = APIRouter()
limiter = Limiter(key_func=get_remote_address,default_limits=["6/minute"])


@router.post("/create_password", tags=["Password"], description="Creates and hash password, with service and description")
async def create_password(
    request: Request,
    password_data: SPassword,
    password_check: Annotated[str, Body(min_length=3,max_length=128)],
    db: Session = Depends(init_db)
):
    if password_data.password != password_check:
        raise HTTPException(400, "Passwords do not match")
    
    if db.query(Password).filter(Password.password == hash_password(password_data.password)).first():
        raise HTTPException(400, "Password already exists")
    
    hashed_password = hash_password(password_data.password)
    new_password = Password(
            service = password_data.service,
            password = hashed_password,
            description = password_data.description
        )
    db.add(new_password)
    db.commit()
    db.refresh(new_password)
    
    return {"status": "password_created"}

@router.post("/password_create",tags=["Password"],description="creates password without hashing")
async def password_create(
    request: Request,
    password_data: SPassword,
    password_check: Annotated[str, Body(min_length=3,max_length=128)],
    db: Session = Depends(init_db)
):
    if password_data.password != password_check:
        raise HTTPException(400, "Passwords do not match")
    
    if db.query(Password).filter(Password.password == hash_password(password_data.password)).first():
        raise HTTPException(400, "Password already exists")
    
    new_password = Password(
            service = password_data.service,
            password = password_data.password,
            description = password_data.description
        )
    db.add(new_password)
    db.commit()
    db.refresh(new_password)
    
    return {"status": "password created without hashing"}


@router.delete("/delete_password", tags=["Password"], description="Deletes password")
async def delete_password(
    password: Annotated[str, Form(min_length=3,max_length=500)],
    db:Session = Depends(init_db)
):
    password_q = db.query(Password).filter(Password.password == password).first()
    if not password_q:
        raise HTTPException(status_code=404,detail="Password not found")

    db.delete(password_q)
    db.commit()
    return {"status":"password deleted"}

@router.get("/get_password", tags=["Password"], description="Get list of passwords")
async def get_passwords(
    db: Session = Depends(init_db)
):
    passwords = db.query(Password).all()
    return passwords

@router.get("/", tags = ["Home"], description="Home page")
async def home():
    return "Hello! Go on /docs, here is interface. Enjoy using it! Bye!"
