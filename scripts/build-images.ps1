# ==============================================================================
# Script de Construcción y Etiquetado de Imágenes para Docker Swarm
# ==============================================================================
Write-Host "==> [1/4] Construyendo imagen de Frontend y Proxy..." -ForegroundColor Cyan
docker build -t petmanager-frontend:latest -f microservices/frontend/Dockerfile .

Write-Host "==> [2/4] Construyendo imagen de Service-Auth..." -ForegroundColor Cyan
docker build -t petmanager-service-auth:latest -f microservices/service-auth/Dockerfile .

Write-Host "==> [3/4] Construyendo imagen de Service-Mascotas..." -ForegroundColor Cyan
docker build -t petmanager-service-mascotas:latest -f microservices/service-mascotas/Dockerfile .

Write-Host "==> [4/4] Construyendo imagen de Service-Analytics (Spark & MapReduce)..." -ForegroundColor Cyan
docker build -t petmanager-service-analytics:latest -f microservices/service-analytics/Dockerfile .

Write-Host "`n[EXITO] Todas las imagenes construidas y listas para Docker Swarm." -ForegroundColor Green
docker images | Select-String "petmanager"
