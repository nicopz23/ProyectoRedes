from fastapi import APIRouter, HTTPException, status
from backend.database import obtener_conexion, obtener_pin_administrador
from backend.schemas import LoginSchema, RegistroUsuarioSchema

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación y Sesión"]
)

@router.post("/login")
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

    # 2. Caso Usuario Normal / Persona Común (por email o nombre)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id, nombre, email, telefono, password
        FROM propietarios
        WHERE LOWER(email) = LOWER(?) OR LOWER(nombre) = LOWER(?)
    """, (usuario_ingresado, usuario_ingresado))
    usuario = cursor.fetchone()
    conexion.close()

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

@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroUsuarioSchema):
    nombre = datos.nombre.strip()
    email = datos.email.strip().lower()
    telefono = datos.telefono.strip() if datos.telefono else None
    password = datos.password.strip()

    if not nombre or not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre, correo electrónico y contraseña son obligatorios"
        )

    if len(password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 4 caracteres"
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Verificar si el correo ya existe
    cursor.execute("SELECT id FROM propietarios WHERE LOWER(email) = LOWER(?)", (email,))
    if cursor.fetchone():
        conexion.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una cuenta registrada con el correo {email}"
        )

    cursor.execute("""
        INSERT INTO propietarios (nombre, email, telefono, password)
        VALUES (?, ?, ?, ?)
    """, (nombre, email, telefono, password))
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()

    return {
        "autenticado": True,
        "rol": "comun",
        "id": nuevo_id,
        "nombre": nombre,
        "email": email,
        "telefono": telefono
    }
