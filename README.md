# Sistema de Gestion de Mascotas

Proyecto de mitad de curso para gestionar mascotas y sus propietarios.

## Descripcion

Aplicacion web para administrar dos entidades relacionadas (1 a N):
* Propietario (id, nombre, telefono, email)
* Mascota (id, nombre, especie, raza, edad, propietario_id)

Tecnologias utilizadas:
* Python 3
* FastAPI
* SQLite
* HTML, CSS, JavaScript (Fetch API)
* Vagrant y VirtualBox (Ubuntu Server)
* Ansible (opcional)

## Estructura del Proyecto

```text
gestion-mascotas/
|-- Vagrantfile
|-- requirements.txt
|-- README.md
|-- backend/
|   |-- main.py
|   |-- database.py
|   |-- schemas.py
|   `-- routes/
|       |-- mascotas.py
|       `-- propietarios.py
|-- frontend/
|   |-- index.html
|   |-- mascotas.html
|   |-- propietarios.html
|   |-- css/
|   |   `-- style.css
|   `-- js/
|       |-- mascotas.js
|       `-- propietarios.js
|-- database/
|   |-- schema.sql
|   `-- mascotas.db
`-- ansible/
    |-- inventory.ini
    `-- playbook.yml
```

## Instrucciones de Ejecucion

### 1. Iniciar con Vagrant y VirtualBox

En la raiz del proyecto ejecutar:

```bash
vagrant up
```

Para conectarse por SSH:

```bash
vagrant ssh
```

### 2. Acceso a la Aplicacion

Una vez iniciado el servidor:
* Pagina principal: http://localhost:8000 o http://192.168.56.20:8000
* Mascotas: http://localhost:8000/mascotas.html
* Propietarios: http://localhost:8000/propietarios.html
* Documentacion Swagger: http://localhost:8000/docs

### 3. Ejecucion Local (Opcional sin Vagrant)

Instalar dependencias:
```bash
pip install -r requirements.txt
```

Iniciar servidor:
```bash
uvicorn backend.main:app --reload
```

## Endpoints de la API REST

### Propietarios
* GET /propietarios - Listar todos los propietarios
* GET /propietarios/{id} - Obtener un propietario por ID
* POST /propietarios - Crear propietario
* PUT /propietarios/{id} - Actualizar propietario
* DELETE /propietarios/{id} - Eliminar propietario

### Mascotas
* GET /mascotas - Listar todas las mascotas
* GET /mascotas/{id} - Obtener una mascota por ID
* POST /mascotas - Crear mascota (valida que el propietario exista)
* PUT /mascotas/{id} - Actualizar mascota
* DELETE /mascotas/{id} - Eliminar mascota

## Base de Datos

SQLite almacena la informacion en `database/mascotas.db`.

Tablas creadas:
* `propietarios`: id, nombre, telefono, email.
* `mascotas`: id, nombre, especie, raza, edad, propietario_id (FOREIGN KEY a propietarios con ON DELETE CASCADE).
