import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import inicializar_base_datos
from backend.routes import propietarios, mascotas, dashboard, admin, auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(
    title="Pet Manager API - Censo y Gestión de Mascotas",
    description="API REST para autenticación, dashboards de censo animal y administración de mascotas y propietarios",
    version="2.2.0"
)

# Permitir CORS para solicitudes desde el servidor de Frontend (Nginx o local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Al arrancar, verificamos esquema y sembrado inicial de datos
inicializar_base_datos()

# Registramos routers de la API
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(propietarios.router)
app.include_router(mascotas.router)

# Servir archivos estáticos del frontend (compatible con modo desarrollo local)
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

@app.get("/")
def inicio(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    return {
        "sistema": "Pet Manager - Sistema de Censo y Gestión de Mascotas",
        "version": "2.2.0",
        "endpoints": {
            "auth": "/auth/login",
            "dashboard": "/dashboard/resumen",
            "mascotas": "/mascotas",
            "propietarios": "/propietarios",
            "admin": "/admin/estado",
            "documentacion": "/docs"
        }
    }

@app.get("/login.html")
def pagina_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/dashboard.html")
def pagina_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/mascotas.html")
def pagina_mascotas():
    return FileResponse(os.path.join(FRONTEND_DIR, "mascotas.html"))

@app.get("/propietarios.html")
def pagina_propietarios():
    return FileResponse(os.path.join(FRONTEND_DIR, "propietarios.html"))
