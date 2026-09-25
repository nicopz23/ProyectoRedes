from pydantic import BaseModel
from typing import Optional

# Modelo para recibir datos de un Propietario
class PropietarioSchema(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None

# Modelo para recibir datos de una Mascota
class MascotaSchema(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    edad: Optional[int] = None
    propietario_id: int
