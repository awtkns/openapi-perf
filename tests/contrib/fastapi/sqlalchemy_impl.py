"""
Code Inspired from https://github.com/awtkns/fastapi-crudrouter/blob/master/fastapi_crudrouter/core/sqlalchemy.py
"""

from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy import Column, String, Float, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ._schemas import Potato, Carrot

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


class PotatoModel(Base):
    __tablename__ = "potatoes"
    id = Column(Integer, primary_key=True, index=True)
    thickness = Column(Float)
    mass = Column(Float)
    color = Column(String)
    type = Column(String)


class CarrotModel(Base):
    __tablename__ = "carrots"
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float)
    color = Column(String)


Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(
    SQLAlchemyCRUDRouter(schema=Potato, db_model=PotatoModel, db=session)
)
app.include_router(
    SQLAlchemyCRUDRouter(schema=Carrot, db_model=CarrotModel, db=session)
)
