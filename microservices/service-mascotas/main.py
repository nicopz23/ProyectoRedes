import os
import sys
from typing import Optional, List

# Permitir importación del módulo común
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from microservices.common.database import (
    inicializar_base_datos,
    ejecutar_consulta,
    ejecutar_escritura,
    poblar_desde_dataset
)
from microservices.common.schemas import (
    MascotaSchema,
    PropietarioSchema
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_base_datos()
    yield

app = FastAPI(
    title="Pet Manager - Microservicio de Mascotas, Propietarios y Analíticas",
    description="Microservicio dedicado a la gestión de animales, tutores y agregaciones analíticas",
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

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "service-mascotas",
        "version": "3.0.0"
    }

# ================= RUTAS DE MASCOTAS =================

@app.get("/mascotas")
def listar_mascotas(
    especie: Optional[str] = Query(default=None, description="Filtrar por especie"),
    propietario_id: Optional[int] = Query(default=None, description="Filtrar por ID de propietario")
):
    query = """
        SELECT 
            m.id, 
            m.nombre, 
            m.especie, 
            m.raza, 
            m.edad, 
            m.sexo, 
            m.vacunado, 
            m.propietario_id,
            p.nombre AS propietario_nombre
        FROM mascotas m
        LEFT JOIN propietarios p ON m.propietario_id = p.id
    """
    condiciones = []
    params = []

    if especie and especie.strip():
        condiciones.append("LOWER(m.especie) = LOWER(?)")
        params.append(especie.strip())

    if propietario_id is not None:
        condiciones.append("m.propietario_id = ?")
        params.append(propietario_id)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    query += " ORDER BY m.id ASC"
    return ejecutar_consulta(query, tuple(params))

@app.get("/mascotas/{mascota_id}")
def obtener_mascota(mascota_id: int):
    mascota = ejecutar_consulta("""
        SELECT m.id, m.nombre, m.especie, m.raza, m.edad, m.sexo, m.vacunado, m.propietario_id,
               p.nombre AS propietario_nombre
        FROM mascotas m
        LEFT JOIN propietarios p ON m.propietario_id = p.id
        WHERE m.id = ?
    """, (mascota_id,), una_fila=True)

    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mascota con ID {mascota_id} no encontrada"
        )
    return mascota

@app.post("/mascotas", status_code=status.HTTP_201_CREATED)
def crear_mascota(datos: MascotaSchema):
    prop = ejecutar_consulta("SELECT id FROM propietarios WHERE id = ?", (datos.propietario_id,), una_fila=True)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El propietario con ID {datos.propietario_id} no existe"
        )

    nuevo_id = ejecutar_escritura("""
        INSERT INTO mascotas (nombre, especie, raza, edad, sexo, vacunado, propietario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datos.nombre.strip(),
        datos.especie.strip(),
        datos.raza.strip() if datos.raza else None,
        datos.edad,
        datos.sexo,
        datos.vacunado,
        datos.propietario_id
    ), retornar_id=True)

    return {"mensaje": "Mascota registrada correctamente", "id": nuevo_id}

@app.put("/mascotas/{mascota_id}")
def actualizar_mascota(mascota_id: int, datos: MascotaSchema):
    mascota = ejecutar_consulta("SELECT id FROM mascotas WHERE id = ?", (mascota_id,), una_fila=True)
    if not mascota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")

    ejecutar_escritura("""
        UPDATE mascotas
        SET nombre = ?, especie = ?, raza = ?, edad = ?, sexo = ?, vacunado = ?, propietario_id = ?
        WHERE id = ?
    """, (
        datos.nombre.strip(),
        datos.especie.strip(),
        datos.raza.strip() if datos.raza else None,
        datos.edad,
        datos.sexo,
        datos.vacunado,
        datos.propietario_id,
        mascota_id
    ))
    return {"mensaje": "Mascota actualizada correctamente", "id": mascota_id}

@app.delete("/mascotas/{mascota_id}")
def eliminar_mascota(mascota_id: int):
    mascota = ejecutar_consulta("SELECT id FROM mascotas WHERE id = ?", (mascota_id,), una_fila=True)
    if not mascota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")

    ejecutar_escritura("DELETE FROM mascotas WHERE id = ?", (mascota_id,))
    return {"mensaje": f"Mascota con ID {mascota_id} eliminada exitosamente"}

# ================= RUTAS DE PROPIETARIOS =================

@app.get("/propietarios")
def listar_propietarios():
    propietarios = ejecutar_consulta("SELECT id, nombre, telefono, email FROM propietarios ORDER BY id ASC")
    for p in propietarios:
        mascotas = ejecutar_consulta("""
            SELECT id, nombre, especie, raza, edad, sexo, vacunado 
            FROM mascotas WHERE propietario_id = ?
        """, (p["id"],))
        p["mascotas"] = mascotas
    return propietarios

@app.get("/propietarios/{propietario_id}")
def obtener_propietario(propietario_id: int):
    p = ejecutar_consulta("SELECT id, nombre, telefono, email FROM propietarios WHERE id = ?", (propietario_id,), una_fila=True)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    p["mascotas"] = ejecutar_consulta("""
        SELECT id, nombre, especie, raza, edad, sexo, vacunado 
        FROM mascotas WHERE propietario_id = ?
    """, (propietario_id,))
    return p

@app.post("/propietarios", status_code=status.HTTP_201_CREATED)
def crear_propietario(datos: PropietarioSchema):
    nuevo_id = ejecutar_escritura("""
        INSERT INTO propietarios (nombre, telefono, email, password)
        VALUES (?, ?, ?, ?)
    """, (datos.nombre.strip(), datos.telefono, datos.email, datos.password or "123456"), retornar_id=True)
    return {"mensaje": "Propietario registrado exitosamente", "id": nuevo_id}

@app.put("/propietarios/{propietario_id}")
def actualizar_propietario(propietario_id: int, datos: PropietarioSchema):
    p = ejecutar_consulta("SELECT id FROM propietarios WHERE id = ?", (propietario_id,), una_fila=True)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    ejecutar_escritura("""
        UPDATE propietarios
        SET nombre = ?, telefono = ?, email = ?
        WHERE id = ?
    """, (datos.nombre.strip(), datos.telefono, datos.email, propietario_id))
    return {"mensaje": "Propietario actualizado exitosamente", "id": propietario_id}

@app.delete("/propietarios/{propietario_id}")
def eliminar_propietario(propietario_id: int):
    p = ejecutar_consulta("SELECT id FROM propietarios WHERE id = ?", (propietario_id,), una_fila=True)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    ejecutar_escritura("DELETE FROM propietarios WHERE id = ?", (propietario_id,))
    return {"mensaje": f"Propietario con ID {propietario_id} y sus mascotas fueron eliminados"}

# ================= RUTAS DE DASHBOARD Y ANALÍTICAS =================

@app.get("/dashboard/resumen")
def resumen_dashboard(propietario_id: Optional[int] = Query(default=None)):
    if propietario_id is not None:
        total_m = ejecutar_consulta("SELECT COUNT(*) AS total FROM mascotas WHERE propietario_id = ?", (propietario_id,), una_fila=True)["total"]
        prom_e = ejecutar_consulta("SELECT AVG(edad) AS promedio FROM mascotas WHERE propietario_id = ? AND edad IS NOT NULL", (propietario_id,), una_fila=True)["promedio"]
        vac_m = ejecutar_consulta("SELECT COUNT(*) AS vac FROM mascotas WHERE propietario_id = ? AND vacunado = 1", (propietario_id,), una_fila=True)["vac"]
        esp_m = ejecutar_consulta("SELECT COUNT(DISTINCT especie) AS esp FROM mascotas WHERE propietario_id = ?", (propietario_id,), una_fila=True)["esp"]

        pct = round((vac_m / total_m * 100), 1) if total_m > 0 else 0
        return {
            "total_mascotas": total_m,
            "total_propietarios": 1 if total_m > 0 else 0,
            "promedio_edad": round(prom_e, 1) if prom_e is not None else 0,
            "vacunados_total": vac_m,
            "porcentaje_vacunados": pct,
            "total_especies": esp_m
        }
    else:
        total_m = ejecutar_consulta("SELECT COUNT(*) AS total FROM mascotas", una_fila=True)["total"]
        total_p = ejecutar_consulta("SELECT COUNT(*) AS total FROM propietarios", una_fila=True)["total"]
        prom_e = ejecutar_consulta("SELECT AVG(edad) AS promedio FROM mascotas WHERE edad IS NOT NULL", una_fila=True)["promedio"]
        vac_m = ejecutar_consulta("SELECT COUNT(*) AS vac FROM mascotas WHERE vacunado = 1", una_fila=True)["vac"]
        esp_m = ejecutar_consulta("SELECT COUNT(DISTINCT especie) AS esp FROM mascotas", una_fila=True)["esp"]

        pct = round((vac_m / total_m * 100), 1) if total_m > 0 else 0
        return {
            "total_mascotas": total_m,
            "total_propietarios": total_p,
            "promedio_edad": round(prom_e, 1) if prom_e is not None else 0,
            "vacunados_total": vac_m,
            "porcentaje_vacunados": pct,
            "total_especies": esp_m
        }

@app.get("/dashboard/distribucion-especie")
def distribucion_por_especie(propietario_id: Optional[int] = Query(default=None)):
    if propietario_id is not None:
        filas = ejecutar_consulta("""
            SELECT especie, COUNT(*) AS cantidad 
            FROM mascotas 
            WHERE propietario_id = ? 
            GROUP BY especie 
            ORDER BY cantidad DESC
        """, (propietario_id,))
    else:
        filas = ejecutar_consulta("""
            SELECT especie, COUNT(*) AS cantidad 
            FROM mascotas 
            GROUP BY especie 
            ORDER BY cantidad DESC
        """)
    return {
        "etiquetas": [f["especie"] for f in filas],
        "valores": [f["cantidad"] for f in filas]
    }

@app.get("/dashboard/distribucion-edad")
def distribucion_por_edad(propietario_id: Optional[int] = Query(default=None)):
    if propietario_id is not None:
        filas = ejecutar_consulta("SELECT edad FROM mascotas WHERE propietario_id = ? AND edad IS NOT NULL", (propietario_id,))
    else:
        filas = ejecutar_consulta("SELECT edad FROM mascotas WHERE edad IS NOT NULL")

    rangos = {"Cachorro / Joven (0-2 años)": 0, "Adulto (3-7 años)": 0, "Senior (8+ años)": 0}
    for f in filas:
        edad = f["edad"]
        if edad <= 2:
            rangos["Cachorro / Joven (0-2 años)"] += 1
        elif edad <= 7:
            rangos["Adulto (3-7 años)"] += 1
        else:
            rangos["Senior (8+ años)"] += 1

    return {"etiquetas": list(rangos.keys()), "valores": list(rangos.values())}

@app.get("/dashboard/estado-vacunacion")
def estado_vacunacion(propietario_id: Optional[int] = Query(default=None)):
    if propietario_id is not None:
        v = ejecutar_consulta("SELECT COUNT(*) AS c FROM mascotas WHERE propietario_id = ? AND vacunado = 1", (propietario_id,), una_fila=True)["c"]
        nv = ejecutar_consulta("SELECT COUNT(*) AS c FROM mascotas WHERE propietario_id = ? AND (vacunado = 0 OR vacunado IS NULL)", (propietario_id,), una_fila=True)["c"]
    else:
        v = ejecutar_consulta("SELECT COUNT(*) AS c FROM mascotas WHERE vacunado = 1", una_fila=True)["c"]
        nv = ejecutar_consulta("SELECT COUNT(*) AS c FROM mascotas WHERE vacunado = 0 OR vacunado IS NULL", una_fila=True)["c"]

    return {
        "etiquetas": ["Vacunados", "Sin Vacunar"],
        "valores": [v, nv]
    }

@app.post("/dashboard/reset-dataset")
def reiniciar_dataset():
    regs = poblar_desde_dataset(reiniciar=True)
    return {"mensaje": "Dataset reiniciado exitosamente", "registros_importados": regs}

if __name__ == "__main__":
    import uvicorn
    puerto = int(os.getenv("PORT", "8002"))
    uvicorn.run("main:app", host="0.0.0.0", port=puerto, reload=True)
