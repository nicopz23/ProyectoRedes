from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import inicializar_base_datos
from backend.routes import propietarios

# Creamos la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Mascotas",
    description="Proyecto de mitad de curso para gestionar mascotas y propietarios"
)

# Permitir comunicación con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Al arrancar, creamos las tablas en SQLite si no existen
inicializar_base_datos()

# Registramos las rutas de propietarios
app.include_router(propietarios.router)

# Endpoint raíz
@app.get("/")
def inicio():
    return {
        "mensaje": "API de Gestión de Mascotas"
    }
