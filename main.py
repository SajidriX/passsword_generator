from fastapi import FastAPI, Form, HTTPException
from typing import Annotated
import uvicorn
from hash_functions import hash_password,verify_password
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Создаем таблицы при старте
    print("🟢 Создаем таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Здесь работает приложение
    yield
    
    # 3. Закрываем соединения при завершении
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

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, port=1222)