import os
import csv
import sys
from typing import List, Dict, Any, Optional

PIN_DEFAULT = "231500"

# Detección de configuración por variables de entorno
DB_TYPE = os.getenv("DB_TYPE", "auto")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "petuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "petpass")
DB_NAME = os.getenv("DB_NAME", "petmanager_db")

# Rutas para SQLite y Dataset
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "mascotas.db")

# Búsqueda del dataset CSV en varias ubicaciones posibles
DATASET_CSV_CANDIDATES = [
    os.path.join(DB_DIR, "dataset_censo_mascotas.csv"),
    os.path.join(BASE_DIR, "dataset_censo_mascotas.csv"),
    "/app/database/dataset_censo_mascotas.csv",
    os.path.abspath("database/dataset_censo_mascotas.csv")
]

DATASET_CSV = None
for candidate in DATASET_CSV_CANDIDATES:
    if os.path.exists(candidate):
        DATASET_CSV = candidate
        break

def es_postgres() -> bool:
    """Determina si la base de datos configurada es PostgreSQL."""
    if DB_TYPE.lower() == "postgres" or DB_HOST != "":
        return True
    return False

def obtener_conexion():
    """Retorna una conexión activa a PostgreSQL o a SQLite."""
    if es_postgres():
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conexion = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
                cursor_factory=RealDictCursor
            )
            conexion.autocommit = True
            return conexion
        except ImportError:
            print("[ALERTA] psycopg2 no está instalado. Usando fallback SQLite.")
        except Exception as e:
            print(f"[ERROR] Conexión a PostgreSQL fallida ({e}). Usando fallback SQLite.")
    
    # Fallback SQLite
    import sqlite3
    os.makedirs(DB_DIR, exist_ok=True)
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

def adaptar_query(query: str, a_postgres: bool) -> str:
    """Adapta sintaxis de placeholders y cláusulas entre SQLite y PostgreSQL."""
    if a_postgres:
        # Reemplazar ? por %s para psycopg2
        query = query.replace("?", "%s")
        # En caso de INSERT OR IGNORE -> ON CONFLICT DO NOTHING
        query = query.replace("INSERT OR IGNORE", "INSERT")
    return query

def ejecutar_consulta(query: str, params: tuple = (), una_fila: bool = False) -> Any:
    """Ejecuta un SELECT y retorna una lista de diccionarios o un diccionario."""
    conexion = obtener_conexion()
    use_pg = es_postgres() and hasattr(conexion, "cursor_factory")
    query_adaptada = adaptar_query(query, use_pg)
    
    cursor = conexion.cursor()
    cursor.execute(query_adaptada, params)
    
    if una_fila:
        fila = cursor.fetchone()
        conexion.close()
        return dict(fila) if fila else None
    
    filas = cursor.fetchall()
    conexion.close()
    return [dict(f) for f in filas]

def ejecutar_escritura(query: str, params: tuple = (), retornar_id: bool = False) -> Optional[int]:
    """Ejecuta un INSERT, UPDATE o DELETE. Opcionalmente retorna el ID generado."""
    conexion = obtener_conexion()
    use_pg = es_postgres() and hasattr(conexion, "cursor_factory")
    
    if use_pg and retornar_id and "returning id" not in query.lower():
        query = query.rstrip().rstrip(";") + " RETURNING id;"
        
    query_adaptada = adaptar_query(query, use_pg)
    cursor = conexion.cursor()
    cursor.execute(query_adaptada, params)
    
    id_generado = None
    if retornar_id:
        if use_pg:
            res = cursor.fetchone()
            id_generado = res["id"] if res else None
        else:
            id_generado = cursor.lastrowid
            
    if not use_pg:
        conexion.commit()
    conexion.close()
    return id_generado

def inicializar_base_datos():
    """Crea las tablas necesarias e inicializa datos base."""
    conexion = obtener_conexion()
    use_pg = es_postgres() and hasattr(conexion, "cursor_factory")
    cursor = conexion.cursor()
    
    if use_pg:
        # Esquema PostgreSQL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS propietarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            telefono VARCHAR(50),
            email VARCHAR(150) UNIQUE,
            password VARCHAR(255) NOT NULL DEFAULT '123456'
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            especie VARCHAR(100) NOT NULL,
            raza VARCHAR(100),
            edad INTEGER,
            sexo VARCHAR(50) DEFAULT 'No especificado',
            vacunado INTEGER DEFAULT 0,
            propietario_id INTEGER NOT NULL REFERENCES propietarios(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            clave VARCHAR(100) PRIMARY KEY,
            valor TEXT NOT NULL
        );
        """)
        cursor.execute("""
        INSERT INTO configuracion (clave, valor)
        VALUES ('admin_pin', %s)
        ON CONFLICT (clave) DO NOTHING;
        """, (PIN_DEFAULT,))
    else:
        # Esquema SQLite
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS propietarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            password TEXT NOT NULL DEFAULT '123456'
        );
        """)
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
        """)
        cursor.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('admin_pin', ?);", (PIN_DEFAULT,))
        conexion.commit()

    # Comprobar si requiere poblar dataset
    cursor.execute("SELECT COUNT(*) AS total FROM mascotas")
    res = cursor.fetchone()
    total = res["total"] if res else 0
    conexion.close()

    if total < 5:
        poblar_desde_dataset(reiniciar=True)

    print(f"[OK] Base de datos ({'PostgreSQL' if use_pg else 'SQLite'}) inicializada correctamente.")

def obtener_pin_administrador() -> str:
    """Devuelve el PIN actual del administrador."""
    res = ejecutar_consulta("SELECT valor FROM configuracion WHERE clave = ?", ("admin_pin",), una_fila=True)
    if res and res.get("valor"):
        return str(res["valor"])
    return PIN_DEFAULT

def actualizar_pin_administrador(nuevo_pin: str) -> bool:
    """Actualiza el PIN del administrador."""
    use_pg = es_postgres()
    if use_pg:
        query = """
            INSERT INTO configuracion (clave, valor)
            VALUES ('admin_pin', %s)
            ON CONFLICT(clave) DO UPDATE SET valor = EXCLUDED.valor;
        """
        ejecutar_escritura(query, (str(nuevo_pin).strip(),))
    else:
        query = """
            INSERT INTO configuracion (clave, valor)
            VALUES ('admin_pin', ?)
            ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor;
        """
        ejecutar_escritura(query, (str(nuevo_pin).strip(),))
    return True

def poblar_desde_dataset(reiniciar: bool = False):
    """Carga los registros del archivo CSV en la base de datos."""
    dataset_file = DATASET_CSV
    if not dataset_file or not os.path.exists(dataset_file):
        print(f"[AVISO] No se encontró el dataset CSV en las rutas estándar.")
        return 0

    if reiniciar:
        ejecutar_escritura("DELETE FROM mascotas;")
        ejecutar_escritura("DELETE FROM propietarios;")

    registros_insertados = 0
    with open(dataset_file, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            nombre_prop = fila["propietario_nombre"].strip()
            prop = ejecutar_consulta("SELECT id FROM propietarios WHERE nombre = ?", (nombre_prop,), una_fila=True)
            if prop:
                prop_id = prop["id"]
            else:
                pwd = fila.get("propietario_password", "123456").strip() or "123456"
                prop_id = ejecutar_escritura("""
                    INSERT INTO propietarios (nombre, telefono, email, password)
                    VALUES (?, ?, ?, ?)
                """, (
                    nombre_prop,
                    fila.get("propietario_telefono", "").strip(),
                    fila.get("propietario_email", "").strip(),
                    pwd
                ), retornar_id=True)

            ejecutar_escritura("""
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

    print(f"[OK] Dataset cargado: {registros_insertados} registros importados.")
    return registros_insertados

