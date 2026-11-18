# Pet Manager - Arquitectura de Microservicios en Docker Swarm

Sistema integral de censo poblacional, control de vacunación y analítica animal municipal desplegado sobre una **arquitectura basada en microservicios**, orquestada mediante **Docker Swarm**, con **procesamiento paralelo distribuido con Apache Spark**, **alta disponibilidad / autorecuperación (self-healing)** y **observabilidad en tiempo real con Prometheus y Grafana**.

---

## 🚀 Inicio Rápido (Un Solo Comando)

Para compilar, orquestar y levantar todo el sistema automáticamente en Windows, abre **PowerShell como Administrador** dentro de la carpeta del proyecto y ejecuta:

```powershell
.\scripts\iniciar.ps1
```

Este script automatizado se encarga de:
1. Validar que Docker Desktop esté activo.
2. Inicializar el cluster de Docker Swarm (`docker swarm init`).
3. Construir y optimizar las imágenes de los microservicios.
4. Desplegar el stack completo (`docker stack deploy -c docker-stack.yml petmanager`).
5. Abrir automáticamente la aplicación en tu navegador web.

Para detener y desmontar todo el cluster en cualquier momento:
```powershell
.\scripts\detener.ps1
```

---

## 🌐 URLs y Puntos de Acceso

| Módulo / Servicio | URL en el Navegador | Descripción y Uso |
| :--- | :--- | :--- |
| **Portal Principal** | [http://localhost/](http://localhost/) | Portal de inicio del sistema Pet Manager |
| **Inicio de Sesión** | [http://localhost/login.html](http://localhost/login.html) | Autenticación de tutores y administrador |
| **Dashboard Analítico** | [http://localhost/dashboard.html](http://localhost/dashboard.html) | KPIs, gráficos interactivos y control de Spark |
| **Catálogo de Mascotas** | [http://localhost/mascotas.html](http://localhost/mascotas.html) | Registro y gestión privada / global de animales |
| **Directorio de Propietarios**| [http://localhost/propietarios.html](http://localhost/propietarios.html) | Perfil de tutor y directorio de tutores |
| **Apache Spark Web UI** | [http://localhost:8080/](http://localhost:8080/) | Monitoreo del Master de Spark y Workers en tiempo real |
| **Prometheus Metrics** | [http://localhost:9090/](http://localhost:9090/) | Servidor de métricas, scraping y consultas PromQL |
| **Grafana Dashboards** | [http://localhost:3000/](http://localhost:3000/) | Dashboards de salud del Swarm, latencia y RPS *(User: `admin` / Pass: `admin`)* |

---

## 🔑 Credenciales de Acceso

| Tipo de Perfil | Usuario / Correo | Contraseña / PIN | Permisos y Alcance |
| :--- | :--- | :--- | :--- |
| **Administrador** | `Admin` | `231500` *(PIN por defecto)* | Control total del censo municipal, cambio de PIN de seguridad, analítica consolidada y reinicio de dataset. |
| **Tutor / Persona Común**| `carlos.gomez@email.com` *(o cualquier email del censo)* | `123456` | Acceso privado exclusivo a sus propias mascotas registradas, métricas privadas y edición de perfil. |

---

## 🏗️ Arquitectura del Sistema

```text
                                [ CLIENTE / NAVEGADOR ]
                                           │
                        (Puerto 80: Ingress Routing Mesh)
                                           ▼
                       ┌──────────────────────────────────────┐
                       │    FRONTEND PROXY INGRESS (Nginx)    │
                       │             (2 Réplicas)             │
                       └──────────────────┬───────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
          ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
          │   SERVICE-AUTH    │ │ SERVICE-MASCOTAS  │ │ SERVICE-ANALYTICS │
          │   (2 Réplicas)    │ │   (2 Réplicas)    │ │   (1 Réplica)     │
          │ Puerto int: 8001  │ │ Puerto int: 8002  │ │ Puerto int: 8003  │
          └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
                    │                     │                     │
                    └──────────────┬──────┴─────────────────────┤
                                   ▼                            ▼
                        ┌─────────────────────┐      ┌─────────────────────┐
                        │   POSTGRESQL DB     │      │ APACHE SPARK CLUSTER│
                        │    (1 Réplica)      │      │  Master + 2 Workers │
                        │  Volumen Persistente│      │ (Procesamiento Par.)│
                        └─────────────────────┘      └─────────────────────┘
                                   ▲
                                   │ (Scraping de métricas cada 5s)
                    ┌──────────────┴──────────────┐
                    │      PILA DE MONITOREO      │
                    │  Prometheus (Puerto 9090)   │
                    │   Grafana  (Puerto 3000)    │
                    └─────────────────────────────┘
```

---

## 📁 Estructura del Repositorio

```text
c:\Proyecto\ProyectoRedes/
|-- docker-stack.yml                    # Definición del Stack de producción para Docker Swarm
|-- docker-compose.yml                  # Definición multi-contenedor para desarrollo local
|-- requirements.txt                    # Dependencias generales del proyecto
|-- README.md                           # Documentación completa y guía de ejecución
|-- microservices/                      # Código fuente desacoplado por servicios
|   |-- common/                         # Módulos transversales compartidos
|   |   |-- database.py                 # Conexión dual (PostgreSQL en Swarm / SQLite local)
|   |   `-- schemas.py                  # Modelos Pydantic de validación
|   |-- service-auth/                   # Microservicio de Autenticación, Roles y PIN
|   |   |-- main.py                     # API REST FastAPI (puerto 8001)
|   |   |-- requirements.txt            # Dependencias específicas
|   |   `-- Dockerfile                  # Contenedor optimizado python:3.11-slim
|   |-- service-mascotas/               # Microservicio de Animales, Tutores y KPIs
|   |   |-- main.py                     # API REST FastAPI (puerto 8002)
|   |   |-- requirements.txt            # Dependencias específicas
|   |   `-- Dockerfile                  # Contenedor optimizado python:3.11-slim
|   |-- service-analytics/              # Microservicio de Procesamiento Paralelo
|   |   |-- main.py                     # API REST FastAPI (puerto 8003)
|   |   |-- analytics_engine.py         # Motor MapReduce y conector a Apache Spark
|   |   |-- requirements.txt            # Dependencias con PySpark
|   |   `-- Dockerfile                  # Contenedor con OpenJDK y Python
|   `-- frontend/                       # Microservicio Web y Reverse Proxy Ingress
|       |-- nginx.conf                  # Proxy inverso con resolución dinámica de DNS (127.0.0.11)
|       `-- Dockerfile                  # Contenedor nginx:alpine
|-- monitoring/                         # Pila de Observabilidad y Métricas
|   |-- prometheus/
|   |   `-- prometheus.yml              # Configuración de scraping automático cada 5s
|   `-- grafana/
|       |-- provisioning/               # Carga automática de datasources y dashboards
|       |   |-- datasources/datasources.yml
|       |   `-- dashboards/dashboards.yml
|       `-- dashboards/
|           `-- petmanager_overview.json # Dashboard integral de tráfico, latencia y salud
|-- database/
|   |-- init_postgres.sql               # DDL e índices para PostgreSQL en Swarm
|   |-- dataset_censo_mascotas.csv      # Dataset oficial inicial de 50 registros
|   `-- schema.sql                      # Esquema SQLite
|-- scripts/                            # Scripts de automatización en PowerShell (Windows)
|   |-- iniciar.ps1                     # Script maestro de compilación y despliegue Swarm
|   |-- detener.ps1                     # Detiene y limpia el stack del Swarm
|   |-- build-images.ps1                # Compila y etiqueta las 4 imágenes Docker
|   |-- deploy-swarm.ps1                # Despliega el stack en Swarm
|   `-- test-resilience.ps1             # Demostración en vivo de tolerancia a fallos
`-- tests/                              # Suite de 19 pruebas automatizadas
```

---

## ⚡ Procesamiento Paralelo Distribuido (Apache Spark & MapReduce)

El sistema incorpora un motor especializado de cómputo distribuido en [`microservices/service-analytics/`](microservices/service-analytics/):
1. **Cluster Apache Spark:** Compuesto por un nodo Maestro (`spark-master`) y **2 nodos Trabajadores (`spark-worker`)** configurados en el cluster Swarm.
2. **Algoritmo MapReduce Paralelo:**
   * **Fase MAP:** Distribuye las particiones de datos entre hilos de ejecución paralelos para clasificar a cada animal según especie, edad y estado inmunológico.
   * **Fase SHUFFLE & SORT:** Agrupa las claves concurrentemente por categoría epidemiológica.
   * **Fase REDUCE:** Agrega los totales, calcula las tasas de vacunación y produce el **Índice de Riesgo Sanitario Municipal**.
3. **Ejecución Interactiva:** Desde [http://localhost/dashboard.html](http://localhost/dashboard.html), al hacer clic en **"🔄 Disparar Job Paralelo"**, se ejecuta el cálculo distribuido en milisegundos y los resultados se reflejan en tiempo real.

---

## 🛡️ Mecanismos de Alta Disponibilidad y Resiliencia (Self-Healing)

1. **Replicación Activa:** Los servicios críticos (`frontend`, `service-auth`, `service-mascotas`, `spark-worker`) operan con **2 réplicas balanceadas**.
2. **Routing Mesh:** Docker Swarm balancea las conexiones entrantes entre los contenedores vivos de forma transparente.
3. **Demostración en Vivo de Auto-Recuperación:**
   Durante la exposición, ejecuta en PowerShell:
   ```powershell
   .\scripts\test-resilience.ps1
   ```
   El script:
   * Identifica una réplica activa de la API.
   * La termina forzosamente (`docker kill`).
   * Realiza una petición web instantánea demostrando **cero tiempo de inactividad** (la petición la absorbe la segunda réplica).
   * Muestra en pantalla cómo Docker Swarm detecta el fallo y levanta un contenedor de reemplazo en cuestión de segundos (**Self-Healing**).

---

## 📊 Monitoreo y Observabilidad en Tiempo Real

* **Prometheus ([http://localhost:9090/](http://localhost:9090/)):** Recolecta métricas cada 5 segundos mediante la librería `prometheus-fastapi-instrumentator` expuesta en `/metrics` en cada microservicio.
* **Grafana ([http://localhost:3000/](http://localhost:3000/)):** Dashboard preconfigurado llamado **Pet Manager - Docker Swarm Overview** que muestra:
  * Semáforo de salud UP/DOWN de cada microservicio.
  * Tasa de Peticiones por Segundo (RPS) en vivo.
  * Latencia media de respuesta (segundos).
  * Distribución de códigos HTTP (200 OK vs 4xx vs 5xx).

---

## 🎤 Guion Sugerido para la Presentación Grupal (15 Minutos)

| Tiempo | Sección | Qué Mostrar y Decir |
| :--- | :--- | :--- |
| **00:00 - 02:00** | **1. Resumen y Objetivo** | Explicar el problema del censo de mascotas municipal, privacidad de datos por tutor y transición de arquitectura monolítica a microservicios en Docker Swarm. |
| **02:00 - 05:00** | **2. Arquitectura y Docker Swarm** | Mostrar el diagrama de arquitectura, explicar el desacoplamiento en 4 microservicios (`frontend`, `service-auth`, `service-mascotas`, `service-analytics`) y el uso de redes Overlay para aislar PostgreSQL. Ejecutar `docker stack services petmanager` para mostrar las réplicas 2/2. |
| **05:00 - 08:00** | **3. Procesamiento Paralelo (Spark)** | Abrir la consola de Spark en [http://localhost:8080/](http://localhost:8080/) mostrando los 2 workers activos. Ir al Dashboard [http://localhost/dashboard.html](http://localhost/dashboard.html) y presionar **"🔄 Disparar Job Paralelo"**, explicando las fases Map, Shuffle y Reduce que calculan el riesgo sanitario. |
| **08:00 - 11:00** | **4. Monitoreo (Prometheus + Grafana)**| Abrir Grafana [http://localhost:3000/](http://localhost:3000/). Mostrar el dashboard preconfigurado con las métricas en vivo de RPS, latencia y disponibilidad de los contenedores. |
| **11:00 - 13:30** | **5. Demostración de Resiliencia en Vivo** | Ejecutar en PowerShell: `.\scripts\test-resilience.ps1`. Mostrar cómo se destruye un contenedor con `docker kill`, el servicio sigue respondiendo sin caída gracias al balanceo de Swarm, y el cluster crea automáticamente una nueva réplica (Self-Healing). |
| **13:30 - 15:00** | **6. Retos Enfrentados y Conclusiones** | Mencionar retos superados: resolución dinámica de DNS en Nginx con `127.0.0.11`, migración de SQLite a PostgreSQL sin bloqueos por concurrencia multi-réplica, e integración de Spark en contenedores. |

---

## 🧪 Pruebas Automatizadas

Para validar toda la suite de 19 pruebas (unitarias, integración y microservicios):

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
*(Resultado: 19 pruebas ejecutadas y aprobadas al 100%).*
