from fastapi import APIRouter, HTTPException, status
from backend.database import obtener_conexion
from backend.schemas import PropietarioSchema

router = APIRouter(
    prefix="/propietarios",
    tags=["Propietarios"]
)

# 1. Obtener todos los propietarios (para vista de administrador)
@router.get("")
def listar_propietarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, telefono, email FROM propietarios ORDER BY id ASC")
    filas = cursor.fetchall()
    
    resultado = []
    for fila in filas:
        propietario_dict = dict(fila)
        cursor.execute("SELECT id, nombre, especie, raza, edad, sexo, vacunado FROM mascotas WHERE propietario_id = ?", (fila["id"],))
        mascotas = [dict(m) for m in cursor.fetchall()]
        propietario_dict["mascotas"] = mascotas
        resultado.append(propietario_dict)

    conexion.close()
    return resultado

# 2. Obtener un solo propietario por su ID (perfil propio o consulta admin)
@router.get("/{propietario_id}")
def obtener_propietario(propietario_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, telefono, email FROM propietarios WHERE id = ?", (propietario_id,))
    fila = cursor.fetchone()

    if not fila:
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Propietario con ID {propietario_id} no fue encontrado"
        )

    propietario_dict = dict(fila)
    cursor.execute("SELECT id, nombre, especie, raza, edad, sexo, vacunado FROM mascotas WHERE propietario_id = ?", (propietario_id,))
    propietario_dict["mascotas"] = [dict(m) for m in cursor.fetchall()]

    conexion.close()
    return propietario_dict

# 3. Crear un nuevo propietario
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_propietario(datos: PropietarioSchema):
    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre del propietario es obligatorio")

    password = datos.password.strip() if datos.password else "123456"

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO propietarios (nombre, telefono, email, password) VALUES (?, ?, ?, ?)",
        (datos.nombre.strip(), datos.telefono, datos.email, password)
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

    cursor.execute("SELECT id, password FROM propietarios WHERE id = ?", (propietario_id,))
    fila = cursor.fetchone()
    if not fila:
        conexion.close()
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Si se especificó una nueva contraseña, actualizarla; si no, mantener la existente
    nueva_password = datos.password.strip() if (datos.password and datos.password.strip()) else fila["password"]

    cursor.execute(
        "UPDATE propietarios SET nombre = ?, telefono = ?, email = ?, password = ? WHERE id = ?",
        (datos.nombre.strip(), datos.telefono, datos.email, nueva_password, propietario_id)
    )
    conexion.commit()
    conexion.close()

    return {
        "id": propietario_id,
        "nombre": datos.nombre.strip(),
        "telefono": datos.telefono,
        "email": datos.email
    }

# 5. Eliminar un propietario (cascada de mascotas)
@router.delete("/{propietario_id}")
def eliminar_propietario(propietario_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre FROM propietarios WHERE id = ?", (propietario_id,))
    propietario = cursor.fetchone()

    if not propietario:
        conexion.close()
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    cursor.execute("DELETE FROM propietarios WHERE id = ?", (propietario_id,))
    conexion.commit()
    conexion.close()

    return {
        "mensaje": f"Propietario '{propietario['nombre']}' eliminado con éxito"
    }
