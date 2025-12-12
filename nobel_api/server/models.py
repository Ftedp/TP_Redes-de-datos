from typing import List, Optional
from pydantic import BaseModel


"- Definimos como deben verse los objetos laureate y prize"
"- Validamos tipos de datos"

class Laureate(BaseModel):
    """"
    persona premiada
    """
    id: int
    firstname: str
    surname: Optional[str] = None
    motivation: str
    share: int

class Prize(BaseModel):
    """"
    premio
    """
    year: int
    category: str
    laureates: Optional[List[Laureate]] = None

class PrizeCreate(BaseModel):
    """
    Modelo para crear un premio nuevo.
    """
    year: int
    category: str
    laureates: Optional[List[Laureate]] = None

