const API_URL = "/mascotas";
const PROPIETARIOS_URL = "/propietarios";

let listaMascotas = [];

// Elementos del DOM
const contenedorLista = document.getElementById("listaMascotas");
const modal = document.getElementById("modalMascota");
const modalTitulo = document.getElementById("modalTitulo");
const formulario = document.getElementById("formularioMascota");
const selectPropietarios = document.getElementById("propietarioId");
const mensajeAlerta = document.getElementById("mensajeAlerta");

// Configurar botones para abrir y cerrar el modal
document.getElementById("btnNuevaMascota").addEventListener("click", () => abrirModal());
document.getElementById("btnCerrarModal").addEventListener("click", cerrarModal);
document.getElementById("btnCancelar").addEventListener("click", cerrarModal);

// Evento para enviar el formulario
formulario.addEventListener("submit", guardarMascota);

// Al cargar la página, traemos los propietarios y las mascotas
document.addEventListener("DOMContentLoaded", () => {
    cargarPropietariosSelect();
    cargarMascotas();
});

// 1. Obtener todas las mascotas de la API (GET)
function cargarMascotas() {
    fetch(API_URL)
        .then(response => response.json())
        .then(data => {
            listaMascotas = data;
            renderizarMascotas(data);
        })
        .catch(error => {
            console.error("Error al cargar mascotas:", error);
            contenedorLista.innerHTML = "<p>Error al conectar con la API.</p>";
        });
}

// 2. Cargar los propietarios en el <select> para asociar la mascota
function cargarPropietariosSelect() {
    fetch(PROPIETARIOS_URL)
        .then(response => response.json())
        .then(propietarios => {
            selectPropietarios.innerHTML = '<option value="">-- Seleccione Propietario --</option>';
            propietarios.forEach(p => {
                const opcion = document.createElement("option");
                opcion.value = p.id;
                opcion.textContent = p.nombre;
                selectPropietarios.appendChild(opcion);
            });
        })
        .catch(error => console.error("Error al cargar propietarios:", error));
}

// 3. Mostrar las tarjetas en el HTML tal como en la guía
function renderizarMascotas(mascotas) {
    if (mascotas.length === 0) {
        contenedorLista.innerHTML = "<p>No hay mascotas registradas actualmente.</p>";
        return;
    }

    contenedorLista.innerHTML = "";

    mascotas.forEach(m => {
        const tarjeta = document.createElement("div");
        tarjeta.className = "tarjeta";

        const nombrePropietario = m.propietario_nombre || `ID: ${m.propietario_id}`;
        const edadTexto = m.edad !== null ? `${m.edad} años` : "Edad no especificada";
        const razaTexto = m.raza ? m.raza : "Sin raza";

        tarjeta.innerHTML = `
            <h3>${m.nombre}</h3>
            <p>${m.especie} - ${razaTexto} - ${edadTexto}</p>
            <p><strong>Propietario:</strong> ${nombrePropietario}</p>
            <div class="acciones">
                <button class="btn btn-secondary" onclick="editarMascota(${m.id})">Editar</button>
                <button class="btn btn-danger" onclick="eliminarMascota(${m.id}, '${m.nombre}')">Eliminar</button>
            </div>
        `;

        contenedorLista.appendChild(tarjeta);
    });
}

// 4. Abrir modal para crear o editar
function abrirModal(mascota = null) {
    formulario.reset();
    document.getElementById("mascotaId").value = "";

    if (mascota) {
        modalTitulo.textContent = "Editar Mascota";
        document.getElementById("mascotaId").value = mascota.id;
        document.getElementById("nombre").value = mascota.nombre;
        document.getElementById("especie").value = mascota.especie;
        document.getElementById("raza").value = mascota.raza || "";
        document.getElementById("edad").value = mascota.edad !== null ? mascota.edad : "";
        document.getElementById("propietarioId").value = mascota.propietario_id;
    } else {
        modalTitulo.textContent = "Registrar Mascota";
    }

    modal.classList.add("activo");
}

function cerrarModal() {
    modal.classList.remove("activo");
}

// 5. Cargar datos en el formulario para editar
function editarMascota(id) {
    const mascota = listaMascotas.find(m => m.id === id);
    if (mascota) {
        abrirModal(mascota);
    }
}

// 6. Guardar mascota (POST para nueva, PUT para editar)
function guardarMascota(e) {
    e.preventDefault();

    const id = document.getElementById("mascotaId").value;
    const nombre = document.getElementById("nombre").value.trim();
    const especie = document.getElementById("especie").value;
    const raza = document.getElementById("raza").value.trim() || null;
    const edadVal = document.getElementById("edad").value;
    const propietarioId = parseInt(document.getElementById("propietarioId").value, 10);

    const edad = edadVal !== "" ? parseInt(edadVal, 10) : null;

    const datos = {
        nombre: nombre,
        especie: especie,
        raza: raza,
        edad: edad,
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
            mostrarMensaje(id ? "Mascota actualizada correctamente" : "Mascota registrada correctamente", true);
            cargarMascotas();
        })
        .catch(error => {
            mostrarMensaje(error.message, false);
        });
}

// 7. Eliminar mascota (DELETE)
function eliminarMascota(id, nombre) {
    if (!confirm(`¿Estás seguro de eliminar a "${nombre}"?`)) {
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

// 8. Mostrar avisos sencillos
function mostrarMensaje(texto, esExito) {
    mensajeAlerta.textContent = texto;
    mensajeAlerta.className = esExito ? "alerta alerta-exito" : "alerta alerta-error";
    mensajeAlerta.style.display = "block";

    setTimeout(() => {
        mensajeAlerta.style.display = "none";
    }, 3500);
}
