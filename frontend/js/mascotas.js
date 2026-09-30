const API_URL = "/mascotas";
const PROPIETARIOS_URL = "/propietarios";

let listaMascotas = [];

// Elementos del DOM
const contenedorLista = document.getElementById("listaMascotas");
const modal = document.getElementById("modalMascota");
const modalTitulo = document.getElementById("modalTitulo");
const formulario = document.getElementById("formularioMascota");
const selectPropietarios = document.getElementById("propietarioId");
const contenedorCampoPropietario = document.getElementById("contenedorCampoPropietario");
const mensajeAlerta = document.getElementById("mensajeAlerta");

const tituloSeccion = document.getElementById("tituloSeccionMascotas");
const subtituloSeccion = document.getElementById("subtituloMascotas");

const inputBuscar = document.getElementById("inputBuscar");
const selectFiltroEspecie = document.getElementById("selectFiltroEspecie");
const selectFiltroVacuna = document.getElementById("selectFiltroVacuna");

// Configurar botones para modal
const btnNuevaMascota = document.getElementById("btnNuevaMascota");
if (btnNuevaMascota) {
    btnNuevaMascota.addEventListener("click", () => abrirModal());
}
document.getElementById("btnCerrarModal").addEventListener("click", cerrarModal);
document.getElementById("btnCancelar").addEventListener("click", cerrarModal);

// Evento para enviar formulario
formulario.addEventListener("submit", guardarMascota);

// Eventos de filtros y búsqueda
if (inputBuscar) inputBuscar.addEventListener("input", filtrarMascotas);
if (selectFiltroEspecie) selectFiltroEspecie.addEventListener("change", filtrarMascotas);
if (selectFiltroVacuna) selectFiltroVacuna.addEventListener("change", filtrarMascotas);

// Escuchar cambios de rol o tutor para refrescar
window.addEventListener("rolCambiado", () => {
    actualizarEncabezadosRol();
    cargarMascotas();
});

window.addEventListener("tutorCambiado", () => {
    actualizarEncabezadosRol();
    cargarMascotas();
});

// Al cargar la página
document.addEventListener("DOMContentLoaded", () => {
    actualizarEncabezadosRol();
    cargarPropietariosSelect();
    cargarMascotas();
});

function actualizarEncabezadosRol() {
    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorNombre = typeof obtenerTutorActivoNombre === "function" ? obtenerTutorActivoNombre() : "Tutor";

    if (tituloSeccion) {
        tituloSeccion.textContent = admin ? "Todas las Mascotas (Administrador)" : `Mis Mascotas (${tutorNombre})`;
    }
    if (subtituloSeccion) {
        subtituloSeccion.textContent = admin 
            ? "Control global y administración de todos los animales censados"
            : "Gestiona únicamente los animales registrados bajo tu cuenta";
    }
}

// 1. Obtener mascotas según el rol activo
function cargarMascotas() {
    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;

    let url = API_URL;
    // Si es persona común, filtramos por su propio propietario_id
    if (!admin) {
        if (!tutorId) {
            contenedorLista.innerHTML = `
                <div style="grid-column: 1 / -1; background: white; padding: 25px; border-radius: 8px; border: 1px dashed #cbd5e1; text-align: center;">
                    <p style="color: #64748b; margin-bottom: 15px;">No has seleccionado un perfil de tutor activo.</p>
                    <button class="btn btn-primary" onclick="abrirModalSeleccionTutor()">Seleccionar o Crear Mi Perfil</button>
                </div>
            `;
            return;
        }
        url = `${API_URL}?propietario_id=${tutorId}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            listaMascotas = data;
            filtrarMascotas();
        })
        .catch(error => {
            console.error("Error al cargar mascotas:", error);
            contenedorLista.innerHTML = "<p>Error al conectar con la API de mascotas.</p>";
        });
}

// 2. Cargar propietarios en el select (para cuando el admin registre)
function cargarPropietariosSelect() {
    fetch(PROPIETARIOS_URL)
        .then(response => response.json())
        .then(propietarios => {
            selectPropietarios.innerHTML = '<option value="">-- Seleccione Propietario --</option>';
            propietarios.forEach(p => {
                const opcion = document.createElement("option");
                opcion.value = p.id;
                opcion.textContent = `${p.nombre} (ID: #${p.id})`;
                selectPropietarios.appendChild(opcion);
            });
        })
        .catch(error => console.error("Error al cargar propietarios:", error));
}

// 3. Filtrar mascotas según búsqueda y selects
function filtrarMascotas() {
    const texto = inputBuscar ? inputBuscar.value.toLowerCase().trim() : "";
    const especie = selectFiltroEspecie ? selectFiltroEspecie.value.toLowerCase() : "";
    const vacuna = selectFiltroVacuna ? selectFiltroVacuna.value : "";

    const filtradas = listaMascotas.filter(m => {
        const coincideTexto = !texto || 
            m.nombre.toLowerCase().includes(texto) || 
            (m.raza && m.raza.toLowerCase().includes(texto)) ||
            (m.propietario_nombre && m.propietario_nombre.toLowerCase().includes(texto));

        const coincideEspecie = !especie || m.especie.toLowerCase() === especie;
        const coincideVacuna = vacuna === "" || String(m.vacunado) === vacuna;

        return coincideTexto && coincideEspecie && coincideVacuna;
    });

    renderizarMascotas(filtradas);
}

// 4. Renderizar tarjetas de mascotas
function renderizarMascotas(mascotas) {
    const admin = typeof esAdministrador === "function" && esAdministrador();

    if (mascotas.length === 0) {
        if (!admin) {
            contenedorLista.innerHTML = `
                <div style="grid-column: 1 / -1; background: white; padding: 30px; border-radius: 8px; border: 1px dashed #cbd5e1; text-align: center;">
                    <p style="color: #64748b; font-size: 1.05rem; margin-bottom: 15px;">Aún no tienes mascotas registradas en tu cuenta.</p>
                    <button class="btn btn-success" onclick="abrirModal()">+ Registrar Mi Primera Mascota</button>
                </div>
            `;
        } else {
            contenedorLista.innerHTML = "<p>No se encontraron mascotas con los criterios seleccionados.</p>";
        }
        return;
    }

    contenedorLista.innerHTML = "";

    mascotas.forEach(m => {
        const tarjeta = document.createElement("div");
        tarjeta.className = "tarjeta";

        const nombrePropietario = m.propietario_nombre || `ID: ${m.propietario_id}`;
        const edadTexto = m.edad !== null ? `${m.edad} año(s)` : "Edad no especificada";
        const razaTexto = m.raza || "Sin raza registrada";
        const sexoTexto = m.sexo || "No especificado";

        const badgeVacuna = m.vacunado === 1
            ? '<span class="badge badge-vacunado">✓ Vacunado</span>'
            : '<span class="badge badge-no-vacunado">⚠ No Vacunado</span>';

        // Tanto el admin como la persona común tienen CRUD sobre sus mascotas mostradas
        const accionesHtml = `
            <div class="acciones">
                <button class="btn btn-secondary" onclick="editarMascota(${m.id})">Editar</button>
                <button class="btn btn-danger" onclick="eliminarMascota(${m.id}, '${m.nombre}')">Eliminar</button>
            </div>
        `;

        tarjeta.innerHTML = `
            <div class="tarjeta-header">
                <h3>${m.nombre}</h3>
                <span class="badge badge-especie">${m.especie}</span>
            </div>
            <div class="tarjeta-detalle">
                <strong>Raza:</strong> ${razaTexto} | <strong>Edad:</strong> ${edadTexto}
            </div>
            <div class="tarjeta-detalle">
                <strong>Sexo:</strong> ${sexoTexto}
            </div>
            <div class="tarjeta-detalle">
                <strong>Estado:</strong> ${badgeVacuna}
            </div>
            <div class="tarjeta-detalle" style="margin-top: 6px;">
                <strong>Tutor:</strong> ${nombrePropietario}
            </div>
            ${accionesHtml}
        `;

        contenedorLista.appendChild(tarjeta);
    });
}

// 5. Modal para crear/editar
function abrirModal(mascota = null) {
    formulario.reset();
    document.getElementById("mascotaId").value = "";

    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;

    // Si es persona común, ocultamos el selector de propietario y lo auto-asignamos
    if (!admin) {
        if (!tutorId) {
            alert("Por favor selecciona primero tu cuenta de tutor.");
            abrirModalSeleccionTutor();
            return;
        }
        contenedorCampoPropietario.style.display = "none";
        selectPropietarios.removeAttribute("required");
        selectPropietarios.value = String(tutorId);
    } else {
        contenedorCampoPropietario.style.display = "block";
        selectPropietarios.setAttribute("required", "required");
    }

    if (mascota) {
        modalTitulo.textContent = "Editar Mascota";
        document.getElementById("mascotaId").value = mascota.id;
        document.getElementById("nombre").value = mascota.nombre;
        document.getElementById("especie").value = mascota.especie;
        document.getElementById("raza").value = mascota.raza || "";
        document.getElementById("edad").value = mascota.edad !== null ? mascota.edad : "";
        document.getElementById("sexo").value = mascota.sexo || "No especificado";
        document.getElementById("vacunado").value = mascota.vacunado !== undefined ? mascota.vacunado : 1;
        selectPropietarios.value = mascota.propietario_id;
    } else {
        modalTitulo.textContent = "Registrar Nueva Mascota";
        document.getElementById("vacunado").value = "1";
        if (!admin && tutorId) {
            selectPropietarios.value = String(tutorId);
        }
    }

    modal.classList.add("activo");
}

function cerrarModal() {
    modal.classList.remove("activo");
}

function editarMascota(id) {
    const mascota = listaMascotas.find(m => m.id === id);
    if (mascota) {
        abrirModal(mascota);
    }
}

// 6. Guardar Mascota (POST / PUT)
function guardarMascota(e) {
    e.preventDefault();

    const admin = typeof esAdministrador === "function" && esAdministrador();
    const tutorId = typeof obtenerTutorActivoId === "function" ? obtenerTutorActivoId() : null;

    const id = document.getElementById("mascotaId").value;
    const nombre = document.getElementById("nombre").value.trim();
    const especie = document.getElementById("especie").value;
    const raza = document.getElementById("raza").value.trim() || null;
    const edadVal = document.getElementById("edad").value;
    const sexo = document.getElementById("sexo").value;
    const vacunado = parseInt(document.getElementById("vacunado").value, 10);

    let propietarioId = parseInt(selectPropietarios.value, 10);
    if (!admin && tutorId) {
        propietarioId = tutorId;
    }

    if (!propietarioId) {
        alert("Debe haber un tutor asociado a la mascota.");
        return;
    }

    const edad = edadVal !== "" ? parseInt(edadVal, 10) : null;

    const datos = {
        nombre: nombre,
        especie: especie,
        raza: raza,
        edad: edad,
        sexo: sexo,
        vacunado: vacunado,
        propietario_id: propietarioId
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
        .then(() => {
            cerrarModal();
            mostrarMensaje(id ? "Mascota actualizada correctamente" : "Mascota registrada exitosamente", true);
            cargarMascotas();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

// 7. Eliminar Mascota (DELETE)
function eliminarMascota(id, nombre) {
    if (!confirm(`¿Confirmas eliminar a "${nombre}"?`)) {
        return;
    }

    fetch(`${API_URL}/${id}`, {
        method: "DELETE"
    })
        .then(response => {
            if (!response.ok) throw new Error("No se pudo eliminar la mascota");
            return response.json();
        })
        .then(() => {
            mostrarMensaje(`Mascota "${nombre}" eliminada`, true);
            cargarMascotas();
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
