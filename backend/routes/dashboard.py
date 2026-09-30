from fastapi import APIRouter, status, Query
from typing import Optional
from backend.database import obtener_conexion, poblar_desde_dataset

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard y Analíticas"]
)

def _sanitizar_id(valor) -> Optional[int]:
    if isinstance(valor, int):
        return valor
    try:
        if isinstance(valor, str) and valor.isdigit():
            return int(valor)
    except Exception:
        pass
    return None

@router.get("/resumen")
def resumen_dashboard(propietario_id: Optional[int] = Query(default=None, description="Filtrar por tutor específico")):
    """Retorna los indicadores clave (KPIs) globales o privados del tutor."""
    prop_id = _sanitizar_id(propietario_id)
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if prop_id is not None:
        cursor.execute("SELECT COUNT(*) AS total FROM mascotas WHERE propietario_id = ?", (prop_id,))
        total_mascotas = cursor.fetchone()["total"]

        total_propietarios = 1 if total_mascotas > 0 else 0

        cursor.execute("SELECT AVG(edad) AS promedio FROM mascotas WHERE propietario_id = ? AND edad IS NOT NULL", (prop_id,))
        promedio_edad = cursor.fetchone()["promedio"]
        promedio_edad = round(promedio_edad, 1) if promedio_edad is not None else 0

        cursor.execute("SELECT COUNT(*) AS vacunados FROM mascotas WHERE propietario_id = ? AND vacunado = 1", (prop_id,))
        total_vacunados = cursor.fetchone()["vacunados"]

        porcentaje_vacunados = round((total_vacunados / total_mascotas * 100), 1) if total_mascotas > 0 else 0

        cursor.execute("SELECT COUNT(DISTINCT especie) AS total_especies FROM mascotas WHERE propietario_id = ?", (prop_id,))
        total_especies = cursor.fetchone()["total_especies"]
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
        total_mascotas = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM propietarios")
        total_propietarios = cursor.fetchone()["total"]

        cursor.execute("SELECT AVG(edad) AS promedio FROM mascotas WHERE edad IS NOT NULL")
        promedio_edad = cursor.fetchone()["promedio"]
        promedio_edad = round(promedio_edad, 1) if promedio_edad is not None else 0

        cursor.execute("SELECT COUNT(*) AS vacunados FROM mascotas WHERE vacunado = 1")
        total_vacunados = cursor.fetchone()["vacunados"]

        porcentaje_vacunados = round((total_vacunados / total_mascotas * 100), 1) if total_mascotas > 0 else 0

        cursor.execute("SELECT COUNT(DISTINCT especie) AS total_especies FROM mascotas")
        total_especies = cursor.fetchone()["total_especies"]

    conexion.close()

    return {
        "total_mascotas": total_mascotas,
        "total_propietarios": total_propietarios,
        "edad_promedio": promedio_edad,
        "total_vacunados": total_vacunados,
        "porcentaje_vacunados": porcentaje_vacunados,
        "total_especies": total_especies
    }

@router.get("/por-especie")
def distribucion_por_especie(propietario_id: Optional[int] = Query(default=None)):
    """Retorna el conteo de mascotas agrupado por especie."""
    prop_id = _sanitizar_id(propietario_id)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    if prop_id is not None:
        cursor.execute("""
            SELECT especie, COUNT(*) AS cantidad
            FROM mascotas
            WHERE propietario_id = ?
            GROUP BY especie
            ORDER BY cantidad DESC
        """, (prop_id,))
    else:
        cursor.execute("""
            SELECT especie, COUNT(*) AS cantidad
            FROM mascotas
            GROUP BY especie
            ORDER BY cantidad DESC
        """)
    filas = cursor.fetchall()
    conexion.close()
    return [{"especie": f["especie"], "cantidad": f["cantidad"]} for f in filas]

@router.get("/por-edad")
def distribucion_por_edad(propietario_id: Optional[int] = Query(default=None)):
    """Retorna la distribución de mascotas por rangos etarios."""
    prop_id = _sanitizar_id(propietario_id)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    filtro_sql = "WHERE propietario_id = ?" if prop_id is not None else ""
    params = (prop_id,) if prop_id is not None else ()
    
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN edad BETWEEN 0 AND 2 THEN 'Cachorros / Jóvenes (0-2 años)'
                WHEN edad BETWEEN 3 AND 7 THEN 'Adultos (3-7 años)'
                WHEN edad >= 8 THEN 'Seniors (8+ años)'
                ELSE 'Sin especificar'
            END AS rango,
            COUNT(*) AS cantidad
        FROM mascotas
        {filtro_sql}
        GROUP BY rango
        ORDER BY cantidad DESC
    """, params)
    filas = cursor.fetchall()
    conexion.close()
    return [{"rango": f["rango"], "cantidad": f["cantidad"]} for f in filas]

@router.get("/top-razas")
def top_razas(propietario_id: Optional[int] = Query(default=None)):
    """Retorna las razas más frecuentes."""
    prop_id = _sanitizar_id(propietario_id)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    if prop_id is not None:
        cursor.execute("""
            SELECT raza, COUNT(*) AS cantidad
            FROM mascotas
            WHERE propietario_id = ? AND raza IS NOT NULL AND TRIM(raza) != ''
            GROUP BY raza
            ORDER BY cantidad DESC
            LIMIT 6
        """, (prop_id,))
    else:
        cursor.execute("""
            SELECT raza, COUNT(*) AS cantidad
            FROM mascotas
            WHERE raza IS NOT NULL AND TRIM(raza) != ''
            GROUP BY raza
            ORDER BY cantidad DESC
            LIMIT 6
        """)
    filas = cursor.fetchall()
    conexion.close()
    return [{"raza": f["raza"], "cantidad": f["cantidad"]} for f in filas]

@router.get("/vacunacion-por-especie")
def vacunacion_por_especie(propietario_id: Optional[int] = Query(default=None)):
    """Retorna el estado de vacunación desagregado por especie."""
    prop_id = _sanitizar_id(propietario_id)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    if prop_id is not None:
        cursor.execute("""
            SELECT 
                especie,
                SUM(CASE WHEN vacunado = 1 THEN 1 ELSE 0 END) AS vacunados,
                SUM(CASE WHEN vacunado = 0 THEN 1 ELSE 0 END) AS no_vacunados
            FROM mascotas
            WHERE propietario_id = ?
            GROUP BY especie
        """, (prop_id,))
    else:
        cursor.execute("""
            SELECT 
                especie,
                SUM(CASE WHEN vacunado = 1 THEN 1 ELSE 0 END) AS vacunados,
                SUM(CASE WHEN vacunado = 0 THEN 1 ELSE 0 END) AS no_vacunados
            FROM mascotas
            GROUP BY especie
        """)
    filas = cursor.fetchall()
    conexion.close()
    return [{
        "especie": f["especie"],
        "vacunados": f["vacunados"],
        "no_vacunados": f["no_vacunados"]
    } for f in filas]

@router.post("/recargar-dataset", status_code=status.HTTP_200_OK)
def recargar_dataset():
    """Acción administrativa para reiniciar la base de datos con el dataset oficial."""
    insertados = poblar_desde_dataset(reiniciar=True)
    return {
        "mensaje": "Dataset oficial del censo cargado con éxito",
        "registros_insertados": insertados
    }
