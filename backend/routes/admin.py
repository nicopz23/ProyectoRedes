from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.database import obtener_pin_administrador, actualizar_pin_administrador

router = APIRouter(
    prefix="/admin",
    tags=["Administración y Seguridad"]
)

class VerificarPinSchema(BaseModel):
    pin: str

class CambiarPinSchema(BaseModel):
    pin_actual: str
    nuevo_pin: str

@router.get("/estado")
def estado_admin():
    return {
        "sistema": "Pet Manager Security",
        "autenticacion_por_pin": True
    }

@router.post("/verificar-pin")
def verificar_pin(datos: VerificarPinSchema):
    pin_guardado = obtener_pin_administrador()
    if datos.pin.strip() != pin_guardado.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN de administrador incorrecto"
        )
    return {
        "valido": True,
        "mensaje": "Acceso de administrador concedido"
    }

@router.post("/cambiar-pin")
def cambiar_pin(datos: CambiarPinSchema):
    pin_guardado = obtener_pin_administrador()
    if datos.pin_actual.strip() != pin_guardado.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El PIN actual no coincide"
        )
    
    nuevo = datos.nuevo_pin.strip()
    if len(nuevo) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nuevo PIN debe tener al menos 4 caracteres"
        )

    actualizar_pin_administrador(nuevo)
    return {
        "mensaje": "PIN de administrador actualizado correctamente"
    }
