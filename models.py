from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey


SQLALCHEMY_DATABASE_URL = "sqlite:///./task.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer,primary_key=True,index=True)
    password = Column(String(500))

def init_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()