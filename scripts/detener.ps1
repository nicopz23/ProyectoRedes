# ==============================================================================
# Pet Manager - Detener y desmontar stack de Docker Swarm
# ==============================================================================
Write-Host "==> Deteniendo y eliminando el stack 'petmanager' de Docker Swarm..." -ForegroundColor Yellow
docker stack rm petmanager
Write-Host "[OK] Stack desmontado exitosamente." -ForegroundColor Green

