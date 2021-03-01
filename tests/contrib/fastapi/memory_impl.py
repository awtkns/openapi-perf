from fastapi import FastAPI
from fastapi_crudrouter import MemoryCRUDRouter

from tests.contrib.fastapi._schemas import Potato, Carrot

app = FastAPI()
app.include_router(MemoryCRUDRouter(schema=Potato))
app.include_router(MemoryCRUDRouter(schema=Carrot))
