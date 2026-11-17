Write-Host "==> Eliminando stack 'petmanager' de Docker Swarm..." -ForegroundColor Yellow
docker stack rm petmanager
Write-Host "[OK] Stack eliminado." -ForegroundColor Green

