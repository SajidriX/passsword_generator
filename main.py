from fastapi import FastAPI, Form, HTTPException, Depends,Request
from fastapi.responses import HTMLResponse
from typing import Annotated
from uvicorn import run
from ariadne import QueryType, make_executable_schema, graphql_sync,MutationType
from ariadne.asgi import GraphQL
from ariadne.explorer import ExplorerGraphiQL
from hash_functions import hash_password,verify_password
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import Base, engine
from passwords.main_passwords import router as password_router
from models import Password,Session,get_db,engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟢 Создаем таблицы в БД...")
    Base.metadata.create_all(bind=engine)
    
    yield
    
    print("🔴 Закрываем соединение с БД...")
    engine.dispose()

app = FastAPI(lifespan=lifespan)


query = QueryType()
mutation = MutationType()


@query.field("getPassword")
def resolve_passwords(*_):
    with get_db() as db:
        try:
            passwords = db.query(Password).all()
            return passwords
        finally:
            db.close()

@query.field("getPasswordByService")
def resolve_password_by_service(_, info, service: str):
    with get_db() as db:
        password = db.query(Password).filter(Password.service == service).first()
        if not password:
            raise Exception("Password not found")
        return password

@query.field("getPasswordById")
def resolve_password_by_id(_, info, id: int):
    with get_db() as db:
        return db.query(Password).filter(Password.id == id).first() 

@mutation.field("passwordCreate")
def resolve_create_passwords(_,info, input):
    with get_db() as db:
        try:
            new_password = Password(
                password = hash_password(input["password"]),
                service = input["service"],
                description = input["description"]
            )

            db.add(new_password)
            db.commit()
            db.refresh(new_password)

            return new_password
        finally:
            db.close()

@mutation.field("passwordMake")
def resolve_make_passwords(_,info,input):
    with get_db() as db:
        try:
            password = Password(
                password = input["password"],
                service = input["service"],
                description = input["description"]
            )

            db.add(password)
            db.commit()
            db.refresh(password)
            return password
        
        finally:
            db.close()

schema = make_executable_schema(
    """
type Password{
    password: String!
    service: String!
    description: String!
}

input PasswordCreate{
    password: String!
    service: String!
    description: String!
}

type Query{
    getPassword: [Password!]!
    getPasswordByService(service: String!): Password
    getPasswordById(id: ID!): Password 
}

type Mutation{
    passwordCreate(input: PasswordCreate!): Password!
    passwordMake (input: PasswordCreate!): Password!
}
    """,
    query,
    mutation
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

@app.post("/graphql", tags=["Password", "GraphQL"],description="GraphQL version")
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

@app.get("/graphql",tags=["GraphQL"])
async def graphql_explorer():
    return HTMLResponse(explorer_html)


app.include_router(password_router)
app.mount("/graphql", GraphQL(schema=schema, debug=True, context_value=lambda req: {"db": Session(bind=engine)}))

if __name__ == "__main__":
    run("main:app", reload=False, port=1222,ws_max_queue=64)