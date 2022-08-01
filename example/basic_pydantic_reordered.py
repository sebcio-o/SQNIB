from pydantic import BaseModel as dupa
from pydantic import BaseModel as XDD
import pydantic
from typing import Optional

class WeirdModel(dupa):
    id: int
    string: str = 'Hello World!'

class User(pydantic.BaseModel):
    ab: int
    ba: int
    bcaaa: int
    c: int
    caa: int
    id1: int
    string1: Optional[str]

class Item(XDD):
    id2: int
    string2: list[str]