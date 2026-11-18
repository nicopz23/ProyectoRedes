import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

# Ajustar ruta para importar módulos comunes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from microservices.common.database import inicializar_base_datos
# Permitir importación directa y flexible
try:
    from analytics_engine import (
        ejecutar_analitica_completa,
        NUM_WORKERS,
        SPARK_MASTER_URL
    )
except ImportError:
    import importlib.util
    _cur_dir = os.path.dirname(os.path.abspath(__file__))
    _spec = importlib.util.spec_from_file_location("analytics_engine", os.path.join(_cur_dir, "analytics_engine.py"))
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    ejecutar_analitica_completa = _mod.ejecutar_analitica_completa
    NUM_WORKERS = _mod.NUM_WORKERS
    SPARK_MASTER_URL = _mod.SPARK_MASTER_URL

_CACHE_RESULTADOS: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_datos()
    # Ejecutar análisis inicial en segundo plano al arrancar
    global _CACHE_RESULTADOS
    try:
        _CACHE_RESULTADOS = ejecutar_analitica_completa()
    except Exception as e:
        print(f"[AVISO] Error al precargar analítica paralela: {e}")
    yield

app = FastAPI(
    title="Pet Manager - Microservicio de Procesamiento Paralelo y Analíticas (Spark / MapReduce)",
    description="Microservicio dedicado a la ejecución distribuida de analíticas sobre el censo de mascotas",
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
        return PlainTextResponse("# HELP petmanager_service_up Status\n# TYPE petmanager_service_up gauge\npetmanager_service_up{service=\"service-analytics\"} 1\n")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "service-analytics",
        "spark_master": SPARK_MASTER_URL,
        "workers_paralelos": NUM_WORKERS
    }

@app.get("/analytics/status")
def status_motor():
    return {
        "sistema": "Motor de Procesamiento Distribuido Pet Manager",
        "herramienta": "Apache Spark & MapReduce",
        "spark_master_url": SPARK_MASTER_URL,
        "hilos_workers_configurados": NUM_WORKERS,
        "estado": "Operativo"
    }

@app.post("/analytics/ejecutar", status_code=status.HTTP_200_OK)
def disparar_job_paralelo():
    """Dispara el procesamiento paralelo/distribuido de inmediato y actualiza los resultados."""
    global _CACHE_RESULTADOS
    _CACHE_RESULTADOS = ejecutar_analitica_completa()
    return {
        "mensaje": "Job de procesamiento paralelo completado exitosamente",
        "detalles": _CACHE_RESULTADOS
    }

@app.get("/analytics/resultados")
def obtener_ultimos_resultados():
    """Retorna los resultados más recientes del cómputo distribuido."""
    global _CACHE_RESULTADOS
    if not _CACHE_RESULTADOS:
        _CACHE_RESULTADOS = ejecutar_analitica_completa()
    return _CACHE_RESULTADOS

if __name__ == "__main__":
    import uvicorn
    puerto = int(os.getenv("PORT", "8003"))
    uvicorn.run("main:app", host="0.0.0.0", port=puerto, reload=True)
