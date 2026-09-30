from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from backend.database import obtener_conexion
from backend.schemas import MascotaSchema

router = APIRouter(
    prefix="/mascotas",
    tags=["Mascotas"]
)

# 1. Obtener mascotas (con soporte para filtrar por especie y por propietario)
@router.get("")
def listar_mascotas(
    especie: Optional[str] = Query(default=None, description="Filtrar por especie"),
    propietario_id: Optional[int] = Query(default=None, description="Filtrar por ID de propietario")
):
    esp = especie if isinstance(especie, str) and especie.strip() else None
    prop_id = propietario_id if isinstance(propietario_id, int) else None
    if isinstance(propietario_id, str) and propietario_id.isdigit():
        prop_id = int(propietario_id)

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
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

    if esp:
        condiciones.append("LOWER(m.especie) = LOWER(?)")
        params.append(esp)

    if prop_id is not None:
        condiciones.append("m.propietario_id = ?")
        params.append(prop_id)

    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)

    query += " ORDER BY m.id ASC"

    cursor.execute(query, params)
    filas = cursor.fetchall()
    conexion.close()
    return [dict(f) for f in filas]

# 2. Obtener una mascota por su ID
@router.get("/{mascota_id}")
def obtener_mascota(mascota_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
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
        WHERE m.id = ?
    """, (mascota_id,))
    fila = cursor.fetchone()
    conexion.close()

    if not fila:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mascota con ID {mascota_id} no fue encontrada"
        )

    return dict(fila)

# 3. Registrar una nueva mascota
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_mascota(datos: MascotaSchema):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre de la mascota es obligatorio")
    
    if not datos.especie.strip():
        raise HTTPException(status_code=400, detail="La especie de la mascota es obligatoria")

    if datos.edad is not None and datos.edad < 0:
        raise HTTPException(status_code=400, detail="La edad debe ser un número positivo mayor o igual a 0")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM propietarios WHERE id = ?", (datos.propietario_id,))
    if not cursor.fetchone():
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se puede registrar: el propietario con ID {datos.propietario_id} no existe"
        )

    cursor.execute("""
        INSERT INTO mascotas (nombre, especie, raza, edad, sexo, vacunado, propietario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datos.nombre.strip(), 
        datos.especie.strip(), 
        datos.raza.strip() if datos.raza else None, 
        datos.edad, 
        datos.sexo if datos.sexo else "No especificado",
        1 if datos.vacunado else 0,
        datos.propietario_id
    ))
    
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()

    return {
        "id": nuevo_id,
        "nombre": datos.nombre.strip(),
        "especie": datos.especie.strip(),
        "raza": datos.raza,
        "edad": datos.edad,
        "sexo": datos.sexo,
        "vacunado": 1 if datos.vacunado else 0,
        "propietario_id": datos.propietario_id
    }

# 4. Actualizar una mascota
@router.put("/{mascota_id}")
def actualizar_mascota(mascota_id: int, datos: MascotaSchema):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre no puede quedar vacío")
    
    if not datos.especie.strip():
        raise HTTPException(status_code=400, detail="La especie no puede quedar vacía")

    if datos.edad is not None and datos.edad < 0:
        raise HTTPException(status_code=400, detail="La edad debe ser mayor o igual a 0")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id FROM mascotas WHERE id = ?", (mascota_id,))
    if not cursor.fetchone():
        conexion.close()
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    cursor.execute("SELECT id FROM propietarios WHERE id = ?", (datos.propietario_id,))
    if not cursor.fetchone():
        conexion.close()
        raise HTTPException(
            status_code=404,
            detail=f"El propietario con ID {datos.propietario_id} no existe"
        )

    cursor.execute("""
        UPDATE mascotas 
        SET nombre = ?, especie = ?, raza = ?, edad = ?, sexo = ?, vacunado = ?, propietario_id = ?
        WHERE id = ?
    """, (
        datos.nombre.strip(), 
        datos.especie.strip(), 
        datos.raza.strip() if datos.raza else None, 
        datos.edad, 
        datos.sexo if datos.sexo else "No especificado",
        1 if datos.vacunado else 0,
        datos.propietario_id, 
        mascota_id
    ))
    
    conexion.commit()
    conexion.close()

    return {
        "id": mascota_id,
        "nombre": datos.nombre.strip(),
        "especie": datos.especie.strip(),
        "raza": datos.raza,
        "edad": datos.edad,
        "sexo": datos.sexo,
        "vacunado": 1 if datos.vacunado else 0,
        "propietario_id": datos.propietario_id
    }

# 5. Eliminar una mascota
@router.delete("/{mascota_id}")
def eliminar_mascota(mascota_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre FROM mascotas WHERE id = ?", (mascota_id,))
    mascota = cursor.fetchone()

    if not mascota:
        conexion.close()
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    cursor.execute("DELETE FROM mascotas WHERE id = ?", (mascota_id,))
    conexion.commit()
    conexion.close()

    return {
        "mensaje": f"Mascota '{mascota['nombre']}' eliminada con éxito"
    }
