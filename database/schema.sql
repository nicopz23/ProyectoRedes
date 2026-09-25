PRAGMA foreign_keys = ON;

-- Tabla propietarios
CREATE TABLE IF NOT EXISTS propietarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    email TEXT
);

-- Tabla mascotas
CREATE TABLE IF NOT EXISTS mascotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    especie TEXT NOT NULL,
    raza TEXT,
    edad INTEGER,
    propietario_id INTEGER NOT NULL,
    FOREIGN KEY (propietario_id)
        REFERENCES propietarios(id)
        ON DELETE CASCADE
);
