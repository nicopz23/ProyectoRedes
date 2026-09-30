from pydantic import BaseModel
from typing import Optional

# Modelo para recibir datos de un Propietario / Usuario
class PropietarioSchema(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = "123456"

# Modelo para Login unificado (Admin con PIN o Usuario con Email/Password)
class LoginSchema(BaseModel):
    usuario: str
    password: str

# Modelo para Registro público de un nuevo Tutor
class RegistroUsuarioSchema(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    password: str

# Modelo para recibir datos de una Mascota
class MascotaSchema(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    edad: Optional[int] = None
    sexo: Optional[str] = "No especificado"
    vacunado: Optional[int] = 0
    propietario_id: int
