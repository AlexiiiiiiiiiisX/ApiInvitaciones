from pydantic import BaseModel
from typing import List, Optional

# Esquema para crear un acompañante
class AccompanistCreate(BaseModel):
    accompanist_name: str

# Esquema para representar un acompañante
class Accompanist(BaseModel):
    id: int
    accompanist_name: str

    class Config:
        from_attributes = True  # Habilita la compatibilidad con ORM (antes `orm_mode = True`)

# Esquema para crear un invitado
class GuestCreate(BaseModel):
    guest_name: str
    confirmation: bool
    quotas: int

# Esquema para actualizar un invitado
class GuestUpdate(BaseModel):
    guest_name: Optional[str] = None
    confirmation: Optional[bool] = None
    quotas: Optional[int] = None

# Esquema para representar un invitado
class Guest(BaseModel):
    id: int
    guest_name: str
    confirmation: bool
    quotas: int
    accompanists: List[Accompanist] = []

    class Config:
        from_attributes = True  # Habilita la compatibilidad con ORM (antes `orm_mode = True`)