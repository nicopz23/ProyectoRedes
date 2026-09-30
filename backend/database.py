import csv
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "mascotas.db")
DATASET_CSV = os.path.join(DB_DIR, "dataset_censo_mascotas.csv")

PIN_DEFAULT = "231500"

def obtener_conexion():
    """Abre y devuelve una conexión a la base de datos SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def inicializar_base_datos():
    """Crea las tablas necesarias y actualiza el esquema si es necesario."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 1. Tabla Propietarios (con contraseña para acceso privado)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS propietarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        password TEXT NOT NULL DEFAULT '123456'
    );
    """)

    # 2. Tabla Mascotas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mascotas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        especie TEXT NOT NULL,
        raza TEXT,
        edad INTEGER,
        sexo TEXT DEFAULT 'No especificado',
        vacunado INTEGER DEFAULT 0,
        propietario_id INTEGER NOT NULL,
        FOREIGN KEY (propietario_id) REFERENCES propietarios (id) ON DELETE CASCADE
    );
    """)

    # 3. Tabla Configuración (para PIN de administrador y otros parámetros del sistema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL
    );
    """)

    # Insertar PIN por defecto si no existe
    cursor.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('admin_pin', ?);", (PIN_DEFAULT,))

    # Migraciones suaves de columnas por compatibilidad
    cursor.execute("PRAGMA table_info(propietarios);")
    cols_prop = [col["name"] for col in cursor.fetchall()]
    if "password" not in cols_prop:
        cursor.execute("ALTER TABLE propietarios ADD COLUMN password TEXT NOT NULL DEFAULT '123456';")

    cursor.execute("PRAGMA table_info(mascotas);")
    cols_masc = [col["name"] for col in cursor.fetchall()]
    if "sexo" not in cols_masc:
        cursor.execute("ALTER TABLE mascotas ADD COLUMN sexo TEXT DEFAULT 'No especificado';")
    if "vacunado" not in cols_masc:
        cursor.execute("ALTER TABLE mascotas ADD COLUMN vacunado INTEGER DEFAULT 0;")

    conexion.commit()

    # Verificar si es necesario sembrar los datos del dataset
    cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
    total = cursor.fetchone()["total"]
    conexion.close()

    if total < 5:
        poblar_desde_dataset(reiniciar=True)

    print("Base de datos SQLite y esquema inicializados correctamente.")

def obtener_pin_administrador() -> str:
    """Devuelve el PIN actual del administrador almacenado en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = 'admin_pin'")
    fila = cursor.fetchone()
    conexion.close()
    if fila and fila["valor"]:
        return str(fila["valor"])
    return PIN_DEFAULT

def actualizar_pin_administrador(nuevo_pin: str) -> bool:
    """Actualiza el PIN del administrador en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO configuracion (clave, valor)
        VALUES ('admin_pin', ?)
        ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor
    """, (str(nuevo_pin).strip(),))
    conexion.commit()
    conexion.close()
    return True

def poblar_desde_dataset(reiniciar: bool = False):
    """Carga los registros del archivo dataset_censo_mascotas.csv en la base de datos."""
    if not os.path.exists(DATASET_CSV):
        print(f"Aviso: No se encontró el archivo de dataset en {DATASET_CSV}")
        return 0

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if reiniciar:
        cursor.execute("DELETE FROM mascotas;")
        cursor.execute("DELETE FROM propietarios;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('mascotas', 'propietarios');")
        conexion.commit()

    registros_insertados = 0
    with open(DATASET_CSV, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            cursor.execute("SELECT id FROM propietarios WHERE nombre = ?", (fila["propietario_nombre"].strip(),))
            prop = cursor.fetchone()
            if prop:
                prop_id = prop["id"]
            else:
                pwd = fila.get("propietario_password", "123456").strip() or "123456"
                cursor.execute("""
                    INSERT INTO propietarios (nombre, telefono, email, password)
                    VALUES (?, ?, ?, ?)
                """, (
                    fila["propietario_nombre"].strip(),
                    fila.get("propietario_telefono", "").strip(),
                    fila.get("propietario_email", "").strip(),
                    pwd
                ))
                prop_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO mascotas (nombre, especie, raza, edad, sexo, vacunado, propietario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                fila["nombre_mascota"].strip(),
                fila["especie"].strip(),
                fila.get("raza", "").strip(),
                int(fila["edad"]) if fila.get("edad") else None,
                fila.get("sexo", "No especificado").strip(),
                int(fila.get("vacunado", 0)),
                prop_id
            ))
            registros_insertados += 1

    conexion.commit()
    conexion.close()
    print(f"Dataset cargado con éxito: {registros_insertados} registros importados.")
    return registros_insertados
