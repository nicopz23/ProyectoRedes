from fastapi import APIRouter, HTTPException, status
from backend.database import obtener_conexion
from backend.schemas import PropietarioSchema

router = APIRouter(
    prefix="/propietarios",
    tags=["Propietarios"]
)

# 1. Obtener todos los propietarios
@router.get("")
def listar_propietarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # Traemos todos los propietarios
    cursor.execute("SELECT * FROM propietarios")
    filas = cursor.fetchall()
    
    # También podemos consultar las mascotas de cada propietario para que el frontend las muestre
    resultado = []
    for fila in filas:
        propietario_dict = dict(fila)
        cursor.execute("SELECT id, nombre, especie, raza, edad FROM mascotas WHERE propietario_id = ?", (fila["id"],))
        mascotas = [dict(m) for m in cursor.fetchall()]
        propietario_dict["mascotas"] = mascotas
        resultado.append(propietario_dict)

    conexion.close()
    return resultado

# 2. Obtener un solo propietario por su ID
@router.get("/{propietario_id}")
def obtener_propietario(propietario_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM propietarios WHERE id = ?", (propietario_id,))
    fila = cursor.fetchone()

    if not fila:
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propietario con ID {propietario_id} no fue encontrado"
        )

    propietario_dict = dict(fila)
    cursor.execute("SELECT id, nombre, especie, raza, edad FROM mascotas WHERE propietario_id = ?", (propietario_id,))
    propietario_dict["mascotas"] = [dict(m) for m in cursor.fetchall()]

    conexion.close()
    return propietario_dict

# 3. Crear un nuevo propietario
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_propietario(datos: PropietarioSchema):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre del propietario es obligatorio")

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO propietarios (nombre, telefono, email) VALUES (?, ?, ?)",
        (datos.nombre.strip(), datos.telefono, datos.email)
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()

    return {
        "id": nuevo_id,
        "nombre": datos.nombre.strip(),
        "telefono": datos.telefono,
        "email": datos.email,
        "mascotas": []
    }

# 4. Actualizar un propietario existente
@router.put("/{propietario_id}")
def actualizar_propietario(propietario_id: int, datos: PropietarioSchema):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre del propietario no puede quedar vacío")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Comprobamos que el propietario exista
    cursor.execute("SELECT * FROM propietarios WHERE id = ?", (propietario_id,))
    if not cursor.fetchone():
        conexion.close()
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    cursor.execute(
        "UPDATE propietarios SET nombre = ?, telefono = ?, email = ? WHERE id = ?",
        (datos.nombre.strip(), datos.telefono, datos.email, propietario_id)
    )
    conexion.commit()
    conexion.close()

    return {
        "id": propietario_id,
        "nombre": datos.nombre.strip(),
        "telefono": datos.telefono,
        "email": datos.email
    }

# 5. Eliminar un propietario
@router.delete("/{propietario_id}")
def eliminar_propietario(propietario_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM propietarios WHERE id = ?", (propietario_id,))
    propietario = cursor.fetchone()

    if not propietario:
        conexion.close()
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Al eliminar al propietario, por ON DELETE CASCADE se borran también sus mascotas
    cursor.execute("DELETE FROM propietarios WHERE id = ?", (propietario_id,))
    conexion.commit()
    conexion.close()

    return {
        "mensaje": f"Propietario con ID {propietario_id} eliminado con éxito"
    }
