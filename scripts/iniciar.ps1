# ==============================================================================
# Pet Manager - Script Maestro de Inicialización Automatizada
# Orquestación completa en Docker Swarm con un solo comando
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host " INICIANDO PET MANAGER EN DOCKER SWARM (ARQUITECTURA DE MICROSERVICIOS)" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Verificar que Docker esté ejecutándose
Write-Host "`n==> [1/4] Verificando Docker Engine..." -ForegroundColor Cyan
try {
    $null = docker info
    Write-Host "[OK] Docker Engine esta activo." -ForegroundColor Green
} catch {
    Write-Host "[ERROR CRITICO] Docker Desktop no esta iniciado." -ForegroundColor Red
    Write-Host "Por favor inicia Docker Desktop en tu equipo y vuelve a ejecutar este script." -ForegroundColor Yellow
    exit 1
}

# 2. Verificar o inicializar el cluster Docker Swarm
Write-Host "`n==> [2/4] Verificando cluster Docker Swarm..." -ForegroundColor Cyan
$swarmStatus = (docker info --format '{{.Swarm.LocalNodeState}}')
if ($swarmStatus -ne "active") {
    Write-Host "==> Inicializando Docker Swarm..." -ForegroundColor Yellow
    docker swarm init
    Write-Host "[OK] Docker Swarm inicializado exitosamente." -ForegroundColor Green
} else {
    Write-Host "[OK] Docker Swarm ya se encuentra activo." -ForegroundColor Green
}

# 3. Construir las imágenes de los microservicios
Write-Host "`n==> [3/4] Construyendo imagenes optimizadas..." -ForegroundColor Cyan
$baseDir = Split-Path -Parent $PSScriptRoot

Write-Host " -> Construyendo Frontend y Proxy Ingress..." -ForegroundColor Gray
docker build -t petmanager-frontend:latest -f "$baseDir/microservices/frontend/Dockerfile" "$baseDir"

Write-Host " -> Construyendo Microservicio de Autenticacion..." -ForegroundColor Gray
docker build -t petmanager-service-auth:latest -f "$baseDir/microservices/service-auth/Dockerfile" "$baseDir"

Write-Host " -> Construyendo Microservicio de Mascotas..." -ForegroundColor Gray
docker build -t petmanager-service-mascotas:latest -f "$baseDir/microservices/service-mascotas/Dockerfile" "$baseDir"

Write-Host " -> Construyendo Microservicio de Analitica Distribuida..." -ForegroundColor Gray
docker build -t petmanager-service-analytics:latest -f "$baseDir/microservices/service-analytics/Dockerfile" "$baseDir"

Write-Host "[OK] Imagenes construidas correctamente." -ForegroundColor Green

# 4. Desplegar el stack completo en Docker Swarm
Write-Host "`n==> [4/4] Desplegando stack 'petmanager' en Docker Swarm..." -ForegroundColor Cyan
docker stack deploy -c "$baseDir/docker-stack.yml" petmanager

Write-Host "`n==> Sincronizando réplicas y enrutamiento (esperando 8 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# 5. Estado final del cluster
Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "   ¡PET MANAGER ESTA COMPLETAMENTE OPERATIVO EN DOCKER SWARM!    " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green

docker stack services petmanager

Write-Host "`n------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host " PUNTOS DE ACCESO EN TU NAVEGADOR:" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host " * Aplicacion Web (Portal):     http://localhost/" -ForegroundColor White
Write-Host " * Inicio de Sesion (Login):    http://localhost/login.html" -ForegroundColor White
Write-Host " * Dashboard Analitico:         http://localhost/dashboard.html" -ForegroundColor White
Write-Host " * Catalogo de Mascotas:        http://localhost/mascotas.html" -ForegroundColor White
Write-Host " * Directorio de Propietarios:  http://localhost/propietarios.html" -ForegroundColor White
Write-Host " * Consola Apache Spark:        http://localhost:8080/" -ForegroundColor White
Write-Host " * Metricas Prometheus:         http://localhost:9090/" -ForegroundColor White
Write-Host " * Dashboards Grafana:          http://localhost:3000/ (admin / admin)" -ForegroundColor White
Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host " CREDENCIALES DE ACCESO:" -ForegroundColor Yellow
Write-Host " - Administrador:  Usuario: Admin | PIN: 231500" -ForegroundColor Gray
Write-Host " - Tutor Ejemplo:  Usuario: carlos.gomez@email.com | Password: 123456" -ForegroundColor Gray
Write-Host "------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host " PRUEBA DE DEMOSTRACION EN VIVO (ALTA DISPONIBILIDAD):" -ForegroundColor Yellow
Write-Host " Ejecuta: .\scripts\test-resilience.ps1" -ForegroundColor Gray
Write-Host "------------------------------------------------------------------`n" -ForegroundColor Cyan

# Abrir el navegador en el inicio
Start-Process "http://localhost/"

