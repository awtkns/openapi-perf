from pydantic import BaseModel


class ORMModel(BaseModel):
    id: int

    class Config:
        orm_mode = True


class Potato(ORMModel):
    thickness: float
    mass: float
    color: str
    type: str


class Carrot(ORMModel):
    length: float
    color: str = "Orange"
