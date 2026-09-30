PRAGMA foreign_keys = ON;

-- Tabla propietarios con contraseña para autenticación
CREATE TABLE IF NOT EXISTS propietarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    email TEXT UNIQUE,
    password TEXT NOT NULL DEFAULT '123456'
);

-- Tabla mascotas
CREATE TABLE IF NOT EXISTS mascotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    especie TEXT NOT NULL,
    raza TEXT,
    edad INTEGER,
    sexo TEXT DEFAULT 'No especificado',
    vacunado INTEGER DEFAULT 0,
    propietario_id INTEGER NOT NULL,
    FOREIGN KEY (propietario_id)
        REFERENCES propietarios(id)
        ON DELETE CASCADE
);

-- Tabla configuración (para parámetros del sistema como el PIN de administrador)
CREATE TABLE IF NOT EXISTS configuracion (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('admin_pin', '231500');
