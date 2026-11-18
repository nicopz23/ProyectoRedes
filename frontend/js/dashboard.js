/**
 * Lógica del Dashboard y Renderizado de Gráficos con Chart.js
 * - Si es Administrador: Visualiza las estadísticas globales de todo el censo.
 * - Si es Persona Común: Visualiza exclusivamente las estadísticas de SUS PROPIAS mascotas.
 */

const API_DASHBOARD = "/dashboard";

let chartEspeciesInstance = null;
let chartEdadesInstance = null;
let chartVacunacionInstance = null;
let chartRazasInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    actualizarTituloDashboard();
    cargarTodosLosDatos();

    const btnRefrescar = document.getElementById("btnRefrescar");
    if (btnRefrescar) {
        btnRefrescar.addEventListener("click", cargarTodosLosDatos);
    }

    const btnRestablecer = document.getElementById("btnRestablecerDataset");
    if (btnRestablecer) {
        btnRestablecer.addEventListener("click", restablecerDataset);
    }

    const btnSpark = document.getElementById("btnEjecutarSpark");
    if (btnSpark) {
        btnSpark.addEventListener("click", ejecutarJobSpark);
    }
});

function obtenerQueryPropietario() {
    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;
    if (!admin && tutorId) {
        return `?propietario_id=${tutorId}`;
    }
    return "";
}

function actualizarTituloDashboard() {
    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorNombre = typeof obtenerTutorActivoNombre === "function" ? obtenerTutorActivoNombre() : "Tutor";

    const h2 = document.querySelector(".encabezado-seccion h2");
    const sub = document.querySelector(".encabezado-seccion .subtitulo");

    if (h2) {
        h2.textContent = admin ? "Dashboard General del Censo Animal" : `Mi Dashboard - ${tutorNombre}`;
    }
    if (sub) {
        sub.textContent = admin 
            ? "Métricas y análisis consolidado de toda la población municipal"
            : "Estadísticas y estado de salud de tus animales de compañía";
    }
}

async function cargarTodosLosDatos() {
    try {
        const query = obtenerQueryPropietario();
        await Promise.all([
            cargarResumen(query),
            cargarGraficoEspecies(query),
            cargarGraficoEdades(query),
            cargarGraficoVacunacion(query),
            cargarGraficoRazas(query),
            cargarAnaliticaSpark()
        ]);
    } catch (error) {
        console.error("Error al cargar datos del dashboard:", error);
    }
}

async function cargarResumen(query) {
    const res = await fetch(`${API_DASHBOARD}/resumen${query}`);
    if (!res.ok) throw new Error("Error al obtener resumen de KPIs");
    const data = await res.json();

    document.getElementById("kpiTotalMascotas").textContent = data.total_mascotas;
    document.getElementById("kpiTotalPropietarios").textContent = data.total_propietarios;
    document.getElementById("kpiEdadPromedio").textContent = `${data.edad_promedio} años`;
    document.getElementById("kpiVacunacion").textContent = `${data.porcentaje_vacunados}%`;
    document.getElementById("kpiVacunacionDetalle").textContent = 
        `${data.total_vacunados} de ${data.total_mascotas} vacunados`;
}

async function cargarGraficoEspecies(query) {
    const res = await fetch(`${API_DASHBOARD}/por-especie${query}`);
    if (!res.ok) return;
    const data = await res.json();

    const labels = data.map(d => d.especie);
    const valores = data.map(d => d.cantidad);

    const ctx = document.getElementById("chartEspecies").getContext("2d");
    if (chartEspeciesInstance) chartEspeciesInstance.destroy();

    chartEspeciesInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels.length > 0 ? labels : ["Sin datos"],
            datasets: [{
                data: valores.length > 0 ? valores : [1],
                backgroundColor: valores.length > 0 
                    ? ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
                    : ["#e2e8f0"],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

async function cargarGraficoEdades(query) {
    const res = await fetch(`${API_DASHBOARD}/por-edad${query}`);
    if (!res.ok) return;
    const data = await res.json();

    const labels = data.map(d => d.rango);
    const valores = data.map(d => d.cantidad);

    const ctx = document.getElementById("chartEdades").getContext("2d");
    if (chartEdadesInstance) chartEdadesInstance.destroy();

    chartEdadesInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Mascotas",
                data: valores,
                backgroundColor: "#3b82f6",
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

async function cargarGraficoVacunacion(query) {
    const res = await fetch(`${API_DASHBOARD}/resumen${query}`);
    if (!res.ok) return;
    const data = await res.json();

    const vacunados = data.total_vacunados;
    const noVacunados = data.total_mascotas - data.total_vacunados;

    const ctx = document.getElementById("chartVacunacion").getContext("2d");
    if (chartVacunacionInstance) chartVacunacionInstance.destroy();

    const hayDatos = data.total_mascotas > 0;

    chartVacunacionInstance = new Chart(ctx, {
        type: "pie",
        data: {
            labels: hayDatos ? ["Vacunados", "No Vacunados / Pendientes"] : ["Sin mascotas"],
            datasets: [{
                data: hayDatos ? [vacunados, noVacunados] : [1],
                backgroundColor: hayDatos ? ["#16a34a", "#ef4444"] : ["#e2e8f0"],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

async function cargarGraficoRazas(query) {
    const res = await fetch(`${API_DASHBOARD}/top-razas${query}`);
    if (!res.ok) return;
    const data = await res.json();

    const labels = data.map(d => d.raza);
    const valores = data.map(d => d.cantidad);

    const ctx = document.getElementById("chartRazas").getContext("2d");
    if (chartRazasInstance) chartRazasInstance.destroy();

    chartRazasInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Mascotas",
                data: valores,
                backgroundColor: "#0d9488",
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

async function restablecerDataset() {
    if (!confirm("¿Deseas reiniciar la base de datos con el dataset original del censo?")) {
        return;
    }

    try {
        const res = await fetch(`${API_DASHBOARD}/recargar-dataset`, { method: "POST" });
        if (!res.ok) throw new Error("Error al reiniciar dataset");
        const data = await res.json();

        const alerta = document.getElementById("mensajeAlerta");
        alerta.textContent = `Éxito: ${data.mensaje} (${data.registros_insertados} registros).`;
        alerta.className = "alerta alerta-exito";
        alerta.style.display = "block";

        setTimeout(() => alerta.style.display = "none", 4000);
        cargarTodosLosDatos();
    } catch (err) {
        alert("Error: " + err.message);
    }
}

async function cargarAnaliticaSpark() {
    try {
        const res = await fetch("/analytics/resultados");
        if (!res.ok) return;
        const data = await res.json();
        renderizarSparkUI(data);
    } catch (err) {
        console.warn("Módulo de analítica Spark/MapReduce no disponible aún:", err);
    }
}

async function ejecutarJobSpark() {
    const btn = document.getElementById("btnEjecutarSpark");
    if (btn) {
        btn.disabled = true;
        btn.textContent = "⏳ Procesando en Paralelo...";
    }

    try {
        const res = await fetch("/analytics/ejecutar", { method: "POST" });
        if (!res.ok) throw new Error("Error en la ejecución distribuida");
        const data = await res.json();
        renderizarSparkUI(data.detalles);

        const alerta = document.getElementById("mensajeAlerta");
        if (alerta) {
            alerta.textContent = `Job paralelo finalizado en ${data.detalles.duracion_ms} ms (${data.detalles.registros_procesados} muestras particionadas).`;
            alerta.className = "alerta alerta-exito";
            alerta.style.display = "block";
            setTimeout(() => alerta.style.display = "none", 4000);
        }
    } catch (err) {
        alert("Fallo al ejecutar Job: " + err.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = "🔄 Disparar Job Paralelo";
        }
    }
}

function renderizarSparkUI(data) {
    if (!data) return;

    const elMotor = document.getElementById("sparkMotor");
    const elTiempo = document.getElementById("sparkTiempo");
    const elMuestras = document.getElementById("sparkMuestras");
    const elWorkers = document.getElementById("sparkWorkers");
    const tabla = document.getElementById("tablaSparkResultados");

    if (elMotor) elMotor.textContent = data.motor || "MapReduce";
    if (elTiempo) elTiempo.textContent = `${data.duracion_ms || 0} ms`;
    if (elMuestras) elMuestras.textContent = data.registros_procesados || 0;
    if (elWorkers) elWorkers.textContent = `${data.workers_activos || 4} Hilos / Particiones`;

    if (tabla && data.resumen_por_especie) {
        let html = "";
        for (const [especie, m] of Object.entries(data.resumen_por_especie)) {
            const riesgoBadge = m.indice_riesgo_sanitario > 4 
                ? `<span style="color: #dc2626; font-weight: bold;">Alto (${m.indice_riesgo_sanitario})</span>`
                : `<span style="color: #16a34a; font-weight: bold;">Bajo (${m.indice_riesgo_sanitario})</span>`;

            html += `
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px; font-weight: 600;">${especie}</td>
                    <td style="padding: 10px;">${m.total_mascotas}</td>
                    <td style="padding: 10px; color: #16a34a;">${m.vacunados}</td>
                    <td style="padding: 10px; color: #dc2626;">${m.no_vacunados}</td>
                    <td style="padding: 10px;">${m.tasa_vacunacion_pct}%</td>
                    <td style="padding: 10px;">${m.edad_promedio} años</td>
                    <td style="padding: 10px;">${riesgoBadge}</td>
                </tr>
            `;
        }
        tabla.innerHTML = html;
    }
}
