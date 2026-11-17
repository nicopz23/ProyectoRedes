# Script de Despliegue en Docker Swarm (Alta Disponibilidad y Resiliencia)
Write-Host "==> Verificando estado del cluster Docker Swarm..." -ForegroundColor Cyan

$swarmState = (docker info --format '{{.Swarm.LocalNodeState}}')
if ($swarmState -ne "active") {
    Write-Host "==> Inicializando Docker Swarm..." -ForegroundColor Yellow
    docker swarm init
}
else {
    Write-Host "[OK] Docker Swarm ya se encuentra activo." -ForegroundColor Green
}

Write-Host "==> Desplegando Stack 'petmanager'..." -ForegroundColor Cyan
docker stack deploy -c docker-stack.yml petmanager

Write-Host "`n==> Esperando estabilizacion de réplicas (10 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`n==> Estado de los servicios desplegados:" -ForegroundColor Green
docker stack services petmanager

Write-Host "`n==> Tareas y contenedores en ejecucion:" -ForegroundColor Cyan
docker stack ps petmanager

