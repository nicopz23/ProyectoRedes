# Script de Construcción y Etiquetado de Imágenes para Docker Swarm
Write-Host "==> [1/3] Construyendo imagen de Frontend y Proxy..." -ForegroundColor Cyan
docker build -t petmanager-frontend:latest -f microservices/frontend/Dockerfile .

Write-Host "==> [2/3] Construyendo imagen de Service-Auth..." -ForegroundColor Cyan
docker build -t petmanager-service-auth:latest -f microservices/service-auth/Dockerfile .

Write-Host "==> [3/3] Construyendo imagen de Service-Mascotas..." -ForegroundColor Cyan
docker build -t petmanager-service-mascotas:latest -f microservices/service-mascotas/Dockerfile .

Write-Host "`n[EXITO] Todas las imagenes construidas y listas para Docker Swarm." -ForegroundColor Green
docker images | Select-String "petmanager"

