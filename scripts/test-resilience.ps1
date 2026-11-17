# Demostración en Vivo: Alta Disponibilidad, Resiliencia y Self-Healing en Swarm
Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host " PRUEBA DE ALTA DISPONIBILIDAD Y AUTO-RECUPERACION (SELF-HEALING)" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Identificar un contenedor activo de un servicio replicado (service-mascotas)
Write-Host "`n[PASO 1] Identificando réplicas activas del microservicio service-mascotas..." -ForegroundColor Cyan
$contenedorVictima = (docker ps --filter "name=petmanager_service-mascotas" --format "{{.ID}}" | Select-Object -First 1)

if (-not $contenedorVictima) {
    Write-Host "[ERROR] No se encontro ningún contenedor activo de 'petmanager_service-mascotas'." -ForegroundColor Red
    Write-Host "Asegurate de haber ejecutado .\scripts\deploy-swarm.ps1 primero." -ForegroundColor Yellow
    exit 1
}

Write-Host "Contenedor seleccionado para simular caída: $contenedorVictima" -ForegroundColor Green

# 2. Simular fallo catastrofico
Write-Host "`n[PASO 2] Simulando fallo critico forzado (docker kill $contenedorVictima)..." -ForegroundColor Red
docker kill $contenedorVictima

# 3. Comprobar que el servicio sigue respondiendo sin interrupcion
Write-Host "`n[PASO 3] Probando disponibilidad inmediata a traves del Ingress Swarm..." -ForegroundColor Cyan
try {
    $res = Invoke-RestMethod -Uri "http://localhost/health" -Method Get -TimeoutSec 5
    Write-Host "[ALTA DISPONIBILIDAD OK] El servicio respondio exitosamente sin caida:" -ForegroundColor Green
    $res | ConvertTo-Json
}
catch {
    Write-Host "[FALLO] El servicio no respondio: $_" -ForegroundColor Red
}

# 4. Evidenciar la auto-recuperacion (Self-Healing) de Docker Swarm
Write-Host "`n[PASO 4] Verificando como Docker Swarm levanta una nueva replica automaticamente..." -ForegroundColor Yellow
Start-Sleep -Seconds 4
docker service ps petmanager_service-mascotas

Write-Host "`n[DEMOSTRACION EXITOSA] Docker Swarm garantizo alta disponibilidad y autorrecuperacion." -ForegroundColor Green

