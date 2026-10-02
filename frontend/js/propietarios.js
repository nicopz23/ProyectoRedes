const API_URL = "/propietarios";
let listaPropietarios = [];

// Elementos del DOM
const contenedorLista = document.getElementById("listaPropietarios");
const modal = document.getElementById("modalPropietario");
const modalTitulo = document.getElementById("modalTitulo");
const formulario = document.getElementById("formularioPropietario");
const mensajeAlerta = document.getElementById("mensajeAlerta");
const inputBuscarPropietario = document.getElementById("inputBuscarPropietario");

const tituloSeccion = document.getElementById("tituloSeccionPropietarios");
const subtituloSeccion = document.getElementById("subtituloPropietarios");
const btnNuevoPropietario = document.getElementById("btnNuevoPropietario");
const btnEditarMiPerfil = document.getElementById("btnEditarMiPerfil");

// Botones de modal
if (btnNuevoPropietario) {
    btnNuevoPropietario.addEventListener("click", () => abrirModal());
}
if (btnEditarMiPerfil) {
    btnEditarMiPerfil.addEventListener("click", editarPerfilPropio);
}

document.getElementById("btnCerrarModal").addEventListener("click", cerrarModal);
document.getElementById("btnCancelar").addEventListener("click", cerrarModal);

formulario.addEventListener("submit", guardarPropietario);
if (inputBuscarPropietario) {
    inputBuscarPropietario.addEventListener("input", filtrarPropietarios);
}

window.addEventListener("rolCambiado", () => {
    actualizarVista();
});

window.addEventListener("tutorCambiado", () => {
    actualizarVista();
});

document.addEventListener("DOMContentLoaded", () => {
    actualizarVista();
});

function actualizarVista() {
    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;

    if (admin) {
        if (tituloSeccion) tituloSeccion.textContent = "Directorio General de Propietarios";
        if (subtituloSeccion) subtituloSeccion.textContent = "Control global de todos los tutores censados en el municipio";
        cargarTodosLosPropietarios();
    } else {
        if (tituloSeccion) tituloSeccion.textContent = "Mi Perfil de Tutor";
        if (subtituloSeccion) subtituloSeccion.textContent = "Tus datos personales y de contacto como tutor responsable";
        cargarPerfilPropio(tutorId);
    }
}

// 1. Cargar perfil exclusivo de la persona común
async function cargarPerfilPropio(tutorId) {
    if (!tutorId) {
        contenedorLista.innerHTML = `
            <div style="grid-column: 1 / -1; background: white; padding: 25px; border-radius: 8px; border: 1px dashed #cbd5e1; text-align: center;">
                <p style="color: #64748b;">No se encontró una sesión activa de tutor.</p>
            </div>
        `;
        return;
    }

    try {
        const res = await fetch(`${API_URL}/${tutorId}`);
        if (!res.ok) throw new Error("No se pudo cargar la información del perfil");
        const p = await res.json();

        const telefonoTexto = p.telefono || "Sin teléfono registrado";
        const emailTexto = p.email || "Sin correo registrado";

        const mascotas = p.mascotas || [];
        const nombresMascotas = mascotas.length > 0
            ? mascotas.map(m => `<span class="badge badge-especie">${m.nombre} (${m.especie})</span>`).join(" ")
            : "<em style='color: #94a3b8;'>Aún no tienes mascotas registradas</em>";

        contenedorLista.innerHTML = `
            <div class="tarjeta" style="grid-column: 1 / -1; max-width: 600px; margin: 0 auto; padding: 25px;">
                <div class="tarjeta-header" style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 15px;">
                    <div>
                        <h3 style="font-size: 1.35rem;">${p.nombre}</h3>
                        <span style="font-size: 0.85rem; color: #64748b;">ID de Tutor: #${p.id}</span>
                    </div>
                    <span class="badge badge-ciudadano">Tutor Activo</span>
                </div>
                <div class="tarjeta-detalle" style="font-size: 1rem; margin-bottom: 10px;">
                    <strong>📞 Teléfono:</strong> ${telefonoTexto}
                </div>
                <div class="tarjeta-detalle" style="font-size: 1rem; margin-bottom: 15px;">
                    <strong>✉️ Correo Electrónico:</strong> ${emailTexto}
                </div>
                <div class="tarjeta-detalle" style="border-top: 1px solid #e2e8f0; padding-top: 15px;">
                    <strong>Mis animales a cargo:</strong>
                    <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
                        ${nombresMascotas}
                    </div>
                </div>
                <div class="acciones" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="editarPropietario(${p.id})">✏️ Actualizar Mis Datos</button>
                </div>
            </div>
        `;
    } catch (err) {
        contenedorLista.innerHTML = `<p style="color: #dc2626;">Error: ${err.message}</p>`;
    }
}

function editarPerfilPropio() {
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;
    if (tutorId) {
        editarPropietario(tutorId);
    }
}

// 2. Cargar todos los propietarios para el Administrador
function cargarTodosLosPropietarios() {
    fetch(API_URL)
        .then(response => response.json())
        .then(data => {
            listaPropietarios = data;
            filtrarPropietarios();
        })
        .catch(error => {
            console.error("Error al cargar propietarios:", error);
            contenedorLista.innerHTML = "<p>Error al conectar con la API de propietarios.</p>";
        });
}

function filtrarPropietarios() {
    const texto = inputBuscarPropietario ? inputBuscarPropietario.value.toLowerCase().trim() : "";
    const filtrados = listaPropietarios.filter(p => {
        if (!texto) return true;
        return (p.nombre && p.nombre.toLowerCase().includes(texto)) ||
               (p.telefono && p.telefono.includes(texto)) ||
               (p.email && p.email.toLowerCase().includes(texto));
    });
    renderizarDirectorioAdmin(filtrados);
}

function renderizarDirectorioAdmin(propietarios) {
    if (propietarios.length === 0) {
        contenedorLista.innerHTML = "<p>No se encontraron propietarios en el censo.</p>";
        return;
    }

    contenedorLista.innerHTML = "";

    propietarios.forEach(p => {
        const tarjeta = document.createElement("div");
        tarjeta.className = "tarjeta";

        const telefonoTexto = p.telefono || "Sin teléfono";
        const emailTexto = p.email || "Sin correo";

        const mascotas = p.mascotas || [];
        const nombresMascotas = mascotas.length > 0
            ? mascotas.map(m => `<span class="badge badge-especie">${m.nombre} (${m.especie})</span>`).join(" ")
            : "<em style='color: #94a3b8;'>Sin mascotas asociadas</em>";

        tarjeta.innerHTML = `
            <div class="tarjeta-header">
                <h3>${p.nombre}</h3>
                <span class="badge badge-ciudadano">#${p.id}</span>
            </div>
            <div class="tarjeta-detalle">
                <strong>📞 Teléfono:</strong> ${telefonoTexto}
            </div>
            <div class="tarjeta-detalle">
                <strong>✉️ Email:</strong> ${emailTexto}
            </div>
            <div class="tarjeta-detalle" style="margin-top: 10px;">
                <strong>Animales a cargo:</strong>
                <div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px;">
                    ${nombresMascotas}
                </div>
            </div>
            <div class="acciones">
                <button class="btn btn-secondary" onclick="editarPropietario(${p.id})">Editar</button>
                <button class="btn btn-danger" onclick="eliminarPropietario(${p.id}, '${p.nombre}')">Eliminar</button>
            </div>
        `;

        contenedorLista.appendChild(tarjeta);
    });
}

// 3. Modal para crear o editar
async function editarPropietario(id) {
    try {
        const res = await fetch(`${API_URL}/${id}`);
        if (!res.ok) throw new Error("No se pudo obtener datos del propietario");
        const p = await res.json();
        abrirModal(p);
    } catch (err) {
        alert(err.message);
    }
}

function abrirModal(propietario = null) {
    formulario.reset();
    document.getElementById("propietarioId").value = "";

    if (propietario) {
        modalTitulo.textContent = "Editar Datos del Tutor";
        document.getElementById("propietarioId").value = propietario.id;
        document.getElementById("nombre").value = propietario.nombre;
        document.getElementById("telefono").value = propietario.telefono || "";
        document.getElementById("email").value = propietario.email || "";
    } else {
        modalTitulo.textContent = "Registrar Nuevo Propietario";
    }

    modal.classList.add("activo");
}

function cerrarModal() {
    modal.classList.remove("activo");
}

// 4. Guardar propietario
function guardarPropietario(e) {
    e.preventDefault();

    const id = document.getElementById("propietarioId").value;
    const nombre = document.getElementById("nombre").value.trim();
    const telefono = document.getElementById("telefono").value.trim() || null;
    const email = document.getElementById("email").value.trim() || null;

    const datos = {
        nombre: nombre,
        telefono: telefono,
        email: email
    };

    const metodo = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/${id}` : API_URL;

    fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    })
        .then(async response => {
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Error al procesar la solicitud");
            }
            return response.json();
        })
        .then(data => {
            cerrarModal();
            mostrarMensaje(id ? "Tutor actualizado correctamente" : "Tutor registrado con éxito", true);

            // Si la persona común editó su propio perfil, actualizamos el nombre activo en UI
            const tutorActivoId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;
            if (String(id) === String(tutorActivoId)) {
                establecerTutorActivo(id, data.nombre);
            }

            actualizarVista();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

// 5. Eliminar propietario (Solo Admin)
function eliminarPropietario(id, nombre) {
    if (!confirm(`¿Deseas eliminar a "${nombre}"? (También se eliminarán sus mascotas vinculadas en cascada)`)) {
        return;
    }

    fetch(`${API_URL}/${id}`, {
        method: "DELETE"
    })
        .then(response => {
            if (!response.ok) throw new Error("No se pudo eliminar el propietario");
            return response.json();
        })
        .then(() => {
            mostrarMensaje(`Propietario "${nombre}" eliminado`, true);
            actualizarVista();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

function mostrarMensaje(texto, esExito) {
    mensajeAlerta.textContent = texto;
    mensajeAlerta.className = esExito ? "alerta alerta-exito" : "alerta alerta-error";
    mensajeAlerta.style.display = "block";

    setTimeout(() => {
        mensajeAlerta.style.display = "none";
    }, 3500);
}
