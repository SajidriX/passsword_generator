from fastapi import FastAPI, Form, HTTPException, Depends,Request
from fastapi.responses import HTMLResponse
from typing import Annotated
import uvicorn
from ariadne import QueryType, make_executable_schema, graphql_sync
from ariadne.asgi import GraphQL
from ariadne.explorer import ExplorerGraphiQL
from hash_functions import hash_password,verify_password
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine
from passwords.main_passwords import router as password_router
from models import Password,Session,get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟢 Создаем таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    
    yield
    
    print("🔴 Закрываем соединение с БД...")
    engine.dispose()

app = FastAPI(lifespan=lifespan)


query = QueryType()


@query.field("getPassword")
def resolve_passwords(*_):
    with get_db() as db:
        try:
            passwords = db.query(Password).all()
            return passwords
        finally:
            db.close()

schema = make_executable_schema(
    """
type Password{
    password: String!
    service: String!
    description: String!
}

type Query{
    getPassword: [Password]
}
    """,
    query
)

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

explorer_html = ExplorerGraphiQL().html(None)

@app.post("/graphql")
async def graphql_route(
    request: Request,
    db: Session = Depends(lambda: Session())
):
    data = await request.json()
    success, result = graphql_sync(
        schema,
        data,
        context_value={"db": db}
    )
    return result if success else {"error": str(result)}

@app.get("/graphql")
async def graphql_explorer():
    return HTMLResponse(explorer_html)


app.include_router(password_router)
app.mount("/graphql", GraphQL(schema=schema, debug=True, ))

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, port=1222)