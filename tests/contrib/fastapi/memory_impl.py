from fastapi import FastAPI
from fastapi_crudrouter import MemoryCRUDRouter

from _schemas import Potato, Carrot

app = FastAPI()
app.include_router(MemoryCRUDRouter(schema=Potato))
app.include_router(MemoryCRUDRouter(schema=Carrot))
