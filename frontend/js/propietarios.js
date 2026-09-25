const API_URL = "/propietarios";
let listaPropietarios = [];

// Elementos del DOM
const contenedorLista = document.getElementById("listaPropietarios");
const modal = document.getElementById("modalPropietario");
const modalTitulo = document.getElementById("modalTitulo");
const formulario = document.getElementById("formularioPropietario");
const mensajeAlerta = document.getElementById("mensajeAlerta");

// Configurar botones para abrir y cerrar el modal
document.getElementById("btnNuevoPropietario").addEventListener("click", () => abrirModal());
document.getElementById("btnCerrarModal").addEventListener("click", cerrarModal);
document.getElementById("btnCancelar").addEventListener("click", cerrarModal);

// Evento para enviar el formulario
formulario.addEventListener("submit", guardarPropietario);

// Al cargar la página, traemos los propietarios
document.addEventListener("DOMContentLoaded", () => {
    cargarPropietarios();
});

// 1. Obtener todos los propietarios de la API (GET)
function cargarPropietarios() {
    fetch(API_URL)
        .then(response => response.json())
        .then(data => {
            listaPropietarios = data;
            renderizarPropietarios(data);
        })
        .catch(error => {
            console.error("Error al cargar propietarios:", error);
            contenedorLista.innerHTML = "<p>Error al conectar con la API.</p>";
        });
}

// 2. Mostrar las tarjetas de propietarios tal como en la guía
function renderizarPropietarios(propietarios) {
    if (propietarios.length === 0) {
        contenedorLista.innerHTML = "<p>No hay propietarios registrados actualmente.</p>";
        return;
    }

    contenedorLista.innerHTML = "";

    propietarios.forEach(p => {
        const tarjeta = document.createElement("div");
        tarjeta.className = "tarjeta";

        const telefonoTexto = p.telefono ? p.telefono : "Sin teléfono";
        const emailTexto = p.email ? p.email : "Sin correo";

        // Listamos los nombres de sus mascotas si tiene
        const mascotas = p.mascotas || [];
        const nombresMascotas = mascotas.length > 0
            ? mascotas.map(m => m.nombre).join(", ")
            : "Ninguna registrada";

        tarjeta.innerHTML = `
            <h3>${p.nombre}</h3>
            <p>${telefonoTexto}</p>
            <p>${emailTexto}</p>
            <p><small><strong>Mascotas asociadas:</strong> ${nombresMascotas}</small></p>
            <div class="acciones">
                <button class="btn btn-secondary" onclick="editarPropietario(${p.id})">Editar</button>
                <button class="btn btn-danger" onclick="eliminarPropietario(${p.id}, '${p.nombre}')">Eliminar</button>
            </div>
        `;

        contenedorLista.appendChild(tarjeta);
    });
}

// 3. Abrir modal para crear o editar
function abrirModal(propietario = null) {
    formulario.reset();
    document.getElementById("propietarioId").value = "";

    if (propietario) {
        modalTitulo.textContent = "Editar Propietario";
        document.getElementById("propietarioId").value = propietario.id;
        document.getElementById("nombre").value = propietario.nombre;
        document.getElementById("telefono").value = propietario.telefono || "";
        document.getElementById("email").value = propietario.email || "";
    } else {
        modalTitulo.textContent = "Registrar Propietario";
    }

    modal.classList.add("activo");
}

function cerrarModal() {
    modal.classList.remove("activo");
}

// 4. Cargar datos en el formulario para editar
function editarPropietario(id) {
    const propietario = listaPropietarios.find(p => p.id === id);
    if (propietario) {
        abrirModal(propietario);
    }
}

// 5. Guardar propietario (POST para nuevo, PUT para editar)
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
        .then(() => {
            cerrarModal();
            mostrarMensaje(id ? "Propietario actualizado correctamente" : "Propietario registrado con éxito", true);
            cargarPropietarios();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

// 6. Eliminar propietario (DELETE)
function eliminarPropietario(id, nombre) {
    if (!confirm(`¿Deseas eliminar a "${nombre}"? (También se eliminarán sus mascotas)`)) {
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
            cargarPropietarios();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

// 7. Mostrar avisos sencillos
function mostrarMensaje(texto, esExito) {
    mensajeAlerta.textContent = texto;
    mensajeAlerta.className = esExito ? "alerta alerta-exito" : "alerta alerta-error";
    mensajeAlerta.style.display = "block";

    setTimeout(() => {
        mensajeAlerta.style.display = "none";
    }, 3500);
}
