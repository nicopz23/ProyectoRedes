-- ==========================================================
-- Pet Manager - Inicialización de Base de Datos PostgreSQL
-- Compatible con Docker Swarm, Alta Disponibilidad y Replicación
-- ==========================================================

-- 1. Tabla de Propietarios / Tutores
CREATE TABLE IF NOT EXISTS propietarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(50),
    email VARCHAR(150) UNIQUE,
    password VARCHAR(255) NOT NULL DEFAULT '123456'
);

-- 2. Tabla de Mascotas
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

-- 3. Tabla de Configuración de Sistema (PIN Administrador, estado)
CREATE TABLE IF NOT EXISTS configuracion (
    clave VARCHAR(100) PRIMARY KEY,
    valor TEXT NOT NULL
);

-- Insertar PIN de Administrador por defecto si no existe
INSERT INTO configuracion (clave, valor)
VALUES ('admin_pin', '231500')
ON CONFLICT (clave) DO NOTHING;

-- Índices para optimización de consultas concurrentes en Swarm
CREATE INDEX IF NOT EXISTS idx_mascotas_propietario ON mascotas(propietario_id);
CREATE INDEX IF NOT EXISTS idx_mascotas_especie ON mascotas(especie);
CREATE INDEX IF NOT EXISTS idx_propietarios_email ON propietarios(email);

