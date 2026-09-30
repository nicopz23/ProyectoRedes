/**
 * Gestión de sesión, autenticación y roles para Pet Manager
 * - Redirige a /login.html si no hay sesión activa.
 * - Soporta Persona Común (acceso privado) y Administrador (control total).
 */

function obtenerSesionActual() {
    const sesionStr = localStorage.getItem("petmanager_sesion");
    if (!sesionStr) return null;
    try {
        return JSON.parse(sesionStr);
    } catch (e) {
        return null;
    }
}

function esAdministrador() {
    const s = obtenerSesionActual();
    return s && s.rol === "admin";
}

function obtenerTutorActivoId() {
    const s = obtenerSesionActual();
    return (s && s.id) ? parseInt(s.id, 10) : null;
}

function obtenerTutorActivoNombre() {
    const s = obtenerSesionActual();
    return s ? s.nombre : "Usuario";
}

function cerrarSesion() {
    localStorage.removeItem("petmanager_sesion");
    localStorage.removeItem("petmanager_rol");
    localStorage.removeItem("petmanager_tutor_id");
    localStorage.removeItem("petmanager_tutor_nombre");
    window.location.href = "/login.html";
}

async function cambiarPinAdmin(pinActual, nuevoPin) {
    try {
        const respuesta = await fetch("/admin/cambiar-pin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pin_actual: pinActual.trim(), nuevo_pin: nuevoPin.trim() })
        });

        if (!respuesta.ok) {
            const err = await respuesta.json();
            throw new Error(err.detail || "Error al cambiar el PIN");
        }

        const data = await respuesta.json();
        return data.mensaje;
    } catch (error) {
        throw error;
    }
}

function aplicarSesionEnUI() {
    const sesion = obtenerSesionActual();
    const admin = esAdministrador();

    // Actualizar indicador en navbar
    const badgeRol = document.getElementById("badgeRol");
    if (badgeRol) {
        if (admin) {
            badgeRol.textContent = "⚙️ Administrador";
            badgeRol.className = "indicador-rol badge badge-admin";
        } else if (sesion) {
            badgeRol.textContent = `👤 ${sesion.nombre}`;
            badgeRol.className = "indicador-rol badge badge-ciudadano";
        }
    }

    // Botones de acción del navbar
    const btnCambiarPin = document.getElementById("btnCambiarPin");
    const btnCerrarSesion = document.getElementById("btnCerrarSesion");

    if (btnCambiarPin) btnCambiarPin.style.display = admin ? "inline-flex" : "none";
    if (btnCerrarSesion) btnCerrarSesion.style.display = "inline-flex";

    // Elementos condicionales
    document.querySelectorAll(".solo-admin").forEach(el => {
        el.style.display = admin ? "" : "none";
    });

    document.querySelectorAll(".solo-comun").forEach(el => {
        el.style.display = admin ? "none" : "";
    });
}

function inyectarModalCambioPin() {
    if (document.getElementById("modalCambiarPin")) return;

    const modalHtml = `
    <!-- Modal para Cambiar PIN de Administrador -->
    <div id="modalCambiarPin" class="modal">
        <div class="modal-contenido" style="max-width: 400px;">
            <div class="modal-header">
                <h3>Cambiar PIN de Administrador</h3>
                <span class="cerrar" onclick="cerrarModalSeguridad('modalCambiarPin')">&times;</span>
            </div>
            <form id="formCambiarPin" onsubmit="procesarCambioPin(event)">
                <div class="campo">
                    <label for="inputPinActual">PIN Actual:</label>
                    <input type="password" id="inputPinActual" required placeholder="PIN actual">
                </div>
                <div class="campo">
                    <label for="inputNuevoPin">Nuevo PIN (mínimo 4 caracteres):</label>
                    <input type="password" id="inputNuevoPin" required placeholder="Nuevo PIN">
                </div>
                <div id="errorCambiarPin" class="alerta alerta-error" style="display: none; padding: 8px;"></div>
                <div id="exitoCambiarPin" class="alerta alerta-exito" style="display: none; padding: 8px;"></div>
                <div class="modal-acciones">
                    <button type="button" class="btn btn-secondary" onclick="cerrarModalSeguridad('modalCambiarPin')">Cancelar</button>
                    <button type="submit" class="btn btn-success">Guardar Nuevo PIN</button>
                </div>
            </form>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modalHtml);
}

function abrirModalSeguridad(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("activo");
}

function cerrarModalSeguridad(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("activo");
}

async function procesarCambioPin(e) {
    e.preventDefault();
    const actual = document.getElementById("inputPinActual").value;
    const nuevo = document.getElementById("inputNuevoPin").value;
    const errorEl = document.getElementById("errorCambiarPin");
    const exitoEl = document.getElementById("exitoCambiarPin");

    errorEl.style.display = "none";
    exitoEl.style.display = "none";

    try {
        const msg = await cambiarPinAdmin(actual, nuevo);
        exitoEl.textContent = msg;
        exitoEl.style.display = "block";
        setTimeout(() => {
            cerrarModalSeguridad("modalCambiarPin");
            document.getElementById("inputPinActual").value = "";
            document.getElementById("inputNuevoPin").value = "";
        }, 1500);
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
    }
}

// Verificación obligatoria de sesión al cargar cualquier página
document.addEventListener("DOMContentLoaded", () => {
    const ruta = window.location.pathname;
    const sesion = obtenerSesionActual();

    // Si no está logueado y no está en la página de login, redirigir a login
    if (!sesion && !ruta.includes("login.html")) {
        window.location.href = "/login.html";
        return;
    }

    inyectarModalCambioPin();
    aplicarSesionEnUI();

    const btnCambiarPin = document.getElementById("btnCambiarPin");
    if (btnCambiarPin) {
        btnCambiarPin.addEventListener("click", () => abrirModalSeguridad("modalCambiarPin"));
    }

    const btnCerrarSesion = document.getElementById("btnCerrarSesion");
    if (btnCerrarSesion) {
        btnCerrarSesion.addEventListener("click", () => cerrarSesion());
    }
});
