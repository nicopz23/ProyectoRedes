# Pet Manager - Sistema de Censo y Gestión de Mascotas

Proyecto de curso (1ª parte) para la asignatura **Redes e Infraestructura 2026-09**.

El sistema da solución a la problemática de monitoreo poblacional, control de vacunación y registro de animales de compañía en un contexto municipal mediante la presentación de **dashboards analíticos interactivos** alimentados por un **dataset preexistente** de censo animal, con autenticación y control estricto de acceso mediante contraseñas y PIN, arquitectura desacoplada de servicios desplegada en **dos servidores** bajo un **nombre de dominio personalizado**.

---

## 1. Características Principales

* **Autenticación y Seguridad Estricta con Login:**
  * **Página de inicio de sesión (`/login.html`):** Los usuarios y administradores deben autenticarse con sus credenciales correspondientes.
  * **Cuenta de Administrador:** Usuario: `Admin`, Contraseña: PIN de acceso (valor predeterminado inicial: `231500`, modificable por el administrador desde su sesión). Tiene control total sobre todas las mascotas y propietarios del municipio.
  * **Persona Común / Tutores:** Usuario: su correo electrónico registrado (ej: `carlos.gomez@email.com`), Contraseña: su contraseña (predeterminada en el dataset: `123456`). También incluye formulario de autoregistro para nuevos tutores.
* **Privacidad Estricta de Mascotas y Dashboard:**
  * La persona común **únicamente ve y gestiona sus propias mascotas** (CRUD exclusivo vinculado por clave foránea). Nunca ve las mascotas ni los datos privados de otros propietarios.
  * En el **Dashboard**, la persona común visualiza las estadísticas y gráficos **exclusivamente de sus propias mascotas**. El administrador visualiza las estadísticas consolidadas de todo el municipio.
* **Dataset Preexistente:** Carga automática inicial de `database/dataset_censo_mascotas.csv` con 50 registros de animales censados y hogares vinculados con contraseñas seguras.
* **Pruebas Automatizadas:** 15 pruebas (unitarias y de integración) ejecutables con `unittest` o `pytest`.
* **Despliegue en 2 Servidores:**
  * `UbuntuServer-Front` (`192.168.56.10`): Servidor web Nginx con proxy inverso.
  * `UbuntuServer-Back` (`192.168.56.20`): Servidor de aplicaciones FastAPI + SQLite.
* **Acceso Directo o por Dominio:** Acceso directo vía `http://192.168.56.20:8000/` o por dominio `http://petmanager.local`.

---

## 2. Credenciales de Acceso

| Tipo de Perfil | Usuario / Correo | Contraseña / PIN | Alcance y Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `Admin` | `231500` *(o nuevo PIN configurado)* | Control global: ve y edita todas las mascotas y propietarios, dashboard municipal completo, cambio de PIN y reinicio de dataset. |
| **Persona Común** | `carlos.gomez@email.com` *(o cualquier email del censo / nuevo registro)* | `123456` *(o la elegida al registrarse)* | Privado: solo ve y gestiona sus propias mascotas, dashboard con métricas de sus animales y edición de sus propios datos de contacto. |

---

## 3. Estructura del Proyecto

```text
c:\ProyectoRedes/
|-- Vagrantfile                     # Despliegue de los 2 servidores (Front y Back)
|-- requirements.txt                # Dependencias (FastAPI, uvicorn, pytest, httpx)
|-- README.md                       # Documentación técnica del proyecto
|-- ENTREGA_FASE1_FASE2.md          # Documento formal de las Fases de Definición y Diseño
|-- peticiones.txt                  # Catálogo de peticiones cURL de prueba
|-- backend/
|   |-- main.py                     # Punto de entrada FastAPI y configuración de routers
|   |-- database.py                 # Conexión SQLite, esquema, contraseñas y dataset
|   |-- schemas.py                  # Modelos Pydantic para validación y auth
|   `-- routes/
|       |-- auth.py                 # Servicio de login y registro de usuarios
|       |-- admin.py                # Servicio de seguridad y cambio de PIN
|       |-- dashboard.py            # Analíticas globales y privadas por tutor
|       |-- mascotas.py             # CRUD de mascotas y filtro por propietario
|       `-- propietarios.py         # Directorio y perfil de tutores
|-- frontend/
|   |-- login.html                  # Pantalla de inicio de sesión y registro
|   |-- index.html                  # Portal principal con control de sesión
|   |-- dashboard.html              # Vista de dashboards analíticos (Chart.js)
|   |-- mascotas.html               # Catálogo privado de mascotas
|   |-- propietarios.html           # Directorio / Mi Perfil de tutor
|   |-- css/
|   |   `-- style.css               # Estilos y diseño responsivo
|   `-- js/
|       |-- roles.js                # Control de sesión, PIN y navegación
|       |-- dashboard.js            # Lógica y renderizado de gráficos filtrados
|       |-- mascotas.js             # Lógica de mascotas privadas y admin
|       `-- propietarios.js         # Lógica de perfil propio y directorio
|-- database/
|   |-- dataset_censo_mascotas.csv  # Dataset preexistente con contraseñas
|   |-- schema.sql                  # Estructura DDL con claves foráneas en cascada
|   `-- mascotas.db                 # Base de datos SQLite
|-- tests/
|   |-- test_unit.py                # Pruebas unitarias de esquemas y analíticas
|   `-- test_integration.py         # Pruebas de integración de auth, dashboard y CRUD
`-- ansible/
    |-- inventory.ini               # Inventario de los dos servidores
    `-- site.yml                    # Playbook de aprovisionamiento
```

---

## 4. Instrucciones de Acceso y Ejecución

### Opción A: Acceso Directo por IP (Recomendado inmediato)

* **Página de Inicio / Login:** [http://192.168.56.20:8000/](http://192.168.56.20:8000/) o [http://192.168.56.20:8000/login.html](http://192.168.56.20:8000/login.html)
* **Documentación interactiva de la API:** [http://192.168.56.20:8000/docs](http://192.168.56.20:8000/docs)

### Opción B: Acceso con Nombre de Dominio (`petmanager.local`)

Para que Windows resuelva el nombre de dominio local sin un servidor DNS público, abre **PowerShell como Administrador** y ejecuta:
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n192.168.56.20 petmanager.local"
```
Luego podrás ingresar a [http://petmanager.local/](http://petmanager.local/).

---

## 5. Ejecución de Pruebas Automatizadas

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
Todas las 15 pruebas unitarias y de integración se ejecutan y certifican el cumplimiento de los requerimientos.
