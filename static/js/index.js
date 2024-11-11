document.addEventListener("DOMContentLoaded", () => {
    const loginButton = document.querySelector("button");

    loginButton.addEventListener("mouseover", () => {
        loginButton.style.backgroundColor = "#a06b5d";
    });

    loginButton.addEventListener("mouseout", () => {
        loginButton.style.backgroundColor = "#8d5a44";
    });

    // Abre el modal
    function openModal() {
        document.getElementById("addWorkerModal").style.display = "block";
    }

    // Cierra el modal
    function closeModal() {
        document.getElementById("addWorkerModal").style.display = "none";
    }

    // Lógica para guardar el trabajador en la base de datos
    function guardarTrabajador(event) {
        event.preventDefault();  // Evitar el comportamiento por defecto del formulario (recargar página)

        const nombre = document.getElementById("nombre").value;
        const puesto = document.getElementById("puesto").value;
        const correo = document.getElementById("correo").value;
        const telefono = document.getElementById("telefono").value;

        // Preparar datos para enviar al backend
        const datosTrabajador = {
            nombre: nombre,
            puesto: puesto,
            correo: correo,
            telefono: telefono
        };

        // Usamos Fetch API para enviar los datos al servidor (Backend Flask)
        fetch('/guardar_trabajador', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datosTrabajador)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Trabajador guardado con éxito');
                closeModal();  // Cerrar el modal después de guardar
            } else {
                alert('Error al guardar trabajador');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
