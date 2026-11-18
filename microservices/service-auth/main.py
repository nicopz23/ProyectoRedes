import os
import sys

# Permitir importación del módulo común
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from microservices.common.database import (
    inicializar_base_datos,
    ejecutar_consulta,
    ejecutar_escritura,
    obtener_pin_administrador,
    actualizar_pin_administrador
)
from microservices.common.schemas import (
    LoginSchema,
    RegistroUsuarioSchema,
    VerificarPinSchema,
    CambiarPinSchema
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_datos()
    yield

app = FastAPI(
    title="Pet Manager - Microservicio de Autenticación y Seguridad",
    description="Microservicio dedicado a login, gestión de credenciales, roles y PIN de administrador",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrumentación con Prometheus para observabilidad
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
except Exception:
    from fastapi.responses import PlainTextResponse
    @app.get("/metrics")
    def fallback_metrics():
        return PlainTextResponse("# HELP petmanager_service_up Status\n# TYPE petmanager_service_up gauge\npetmanager_service_up{service=\"service-auth\"} 1\n")

# Endpoint de Health Check (vital para Docker Swarm y Prometheus)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "service-auth",
        "version": "3.0.0"
    }

# ================= RUTAS DE AUTENTICACIÓN =================

@app.post("/auth/login")
def login(datos: LoginSchema):
    usuario_ingresado = datos.usuario.strip()
    password_ingresada = datos.password.strip()

    # 1. Caso Administrador
    if usuario_ingresado.lower() == "admin":
        pin_actual = obtener_pin_administrador()
        if password_ingresada != pin_actual:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="PIN de administrador incorrecto"
            )
        return {
            "autenticado": True,
            "rol": "admin",
            "id": None,
            "nombre": "Administrador",
            "email": "admin@petmanager.local"
        }

    # 2. Caso Usuario Común / Tutor
    usuario = ejecutar_consulta("""
        SELECT id, nombre, email, telefono, password
        FROM propietarios
        WHERE LOWER(email) = LOWER(?) OR LOWER(nombre) = LOWER(?)
    """, (usuario_ingresado, usuario_ingresado), una_fila=True)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado. Verifica tu correo o regístrate."
        )

    if usuario["password"] != password_ingresada:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta."
        )

    return {
        "autenticado": True,
        "rol": "comun",
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "telefono": usuario["telefono"]
    }

@app.post("/auth/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: RegistroUsuarioSchema):
    nombre = datos.nombre.strip()
    email = datos.email.strip().lower()
    pwd = datos.password.strip()

    if not nombre or not email or not pwd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre, email y contraseña son obligatorios."
        )

    existente = ejecutar_consulta("SELECT id FROM propietarios WHERE LOWER(email) = LOWER(?)", (email,), una_fila=True)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta registrada con este correo electrónico."
        )

    nuevo_id = ejecutar_escritura("""
        INSERT INTO propietarios (nombre, email, telefono, password)
        VALUES (?, ?, ?, ?)
    """, (nombre, email, datos.telefono, pwd), retornar_id=True)

    return {
        "mensaje": "Usuario registrado exitosamente",
        "rol": "comun",
        "id": nuevo_id,
        "nombre": nombre,
        "email": email
    }

@app.get("/auth/verificar")
def verificar_sesion():
    return {"activo": True, "servicio": "service-auth"}

# ================= RUTAS DE ADMINISTRACIÓN Y PIN =================

@app.get("/admin/estado")
def estado_admin():
    return {
        "sistema": "Pet Manager Security Swarm",
        "autenticacion_por_pin": True,
        "servicio": "service-auth"
    }

@app.post("/admin/verificar-pin")
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

@app.post("/admin/cambiar-pin")
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

if __name__ == "__main__":
    import uvicorn
    puerto = int(os.getenv("PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=puerto, reload=True)
