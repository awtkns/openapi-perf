from pydantic import BaseModel


class ORMModel(BaseModel):
    id: int

    class Config:
        orm_mode = True


class Potato(BaseModel):
    thickness: float
    mass: float
    color: str
    type: str


class Carrot(BaseModel):
    length: float
    color: str = 'Orange'
