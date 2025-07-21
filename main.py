from fastapi import FastAPI, Form, HTTPException
from typing import Annotated
import uvicorn
from hash_functions import hash_password,verify_password
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine
from passwords.main_passwords import router as password_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟢 Создаем таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    
    yield
    
    print("🔴 Закрываем соединение с БД...")
    engine.dispose()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://127.0.0.1:1222",  # Основной домен API
    "http://localhost:1222",   # Альтернативный адрес
    "http://localhost:3002",   # Для фронтенда (React/Vue)
    "http://127.0.0.1:3002",   # Альтернативный адрес фронтенда
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(password_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, port=1222)