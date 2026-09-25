import sqlite3
import os

# Ruta donde se guardará la base de datos dentro de la carpeta database/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "mascotas.db")

def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    conexion = sqlite3.connect(DB_PATH)
    # Permite acceder a las columnas como si fueran diccionarios: fila["nombre"]
    conexion.row_factory = sqlite3.Row
    # Activamos el soporte de claves foráneas en SQLite
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_base_datos():
    conexion = obtener_conexion() # Obtiene la conexión a la base de datos
    cursor = conexion.cursor()

    # 1. Tabla Propietarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS propietarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT
    );
    """)

    # 2. Tabla Mascotas (con foreign key hacia propietarios)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mascotas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        especie TEXT NOT NULL,
        raza TEXT,
        edad INTEGER,
        propietario_id INTEGER NOT NULL,
        FOREIGN KEY (propietario_id) REFERENCES propietarios (id) ON DELETE CASCADE
    );
    """)

    conexion.commit() # Guarda los cambios
    conexion.close()  # Cierra la conexión
    print("Base de datos SQLite y tablas inicializadas con éxito.")
