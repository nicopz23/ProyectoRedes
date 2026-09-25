import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import inicializar_base_datos
from backend.routes import propietarios, mascotas

# Directorio del frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Creamos la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Mascotas",
    description="Proyecto de mitad de curso para gestionar mascotas y propietarios"
)

# Permitir comunicación con el frontend sin seguridad por ahora
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Al arrancar, creamos las tablas en SQLite si no existen
inicializar_base_datos()

# Registramos las rutas de la API
app.include_router(propietarios.router)
app.include_router(mascotas.router)

# Montamos las carpetas de archivos estáticos (CSS y JS)
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

# Endpoint raíz
@app.get("/")
def inicio(request: Request):
    # Si la petición viene de un navegador web, sirve index.html
    if "text/html" in request.headers.get("accept", ""):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    # Si la petición pide JSON o curl, devuelve el mensaje de la API
    return {
        "mensaje": "API de Gestión de Mascotas"
    }

@app.get("/mascotas.html")
def pagina_mascotas():
    return FileResponse(os.path.join(FRONTEND_DIR, "mascotas.html"))

@app.get("/propietarios.html")
def pagina_propietarios():
    return FileResponse(os.path.join(FRONTEND_DIR, "propietarios.html"))
