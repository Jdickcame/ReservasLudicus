document.addEventListener('DOMContentLoaded', function () {
    
    // ==========================================================
    // === PARTE 1: LÓGICA DE "ADICIONALES"
    // ==========================================================
    
    const selectAdicional = document.getElementById('select-adicional');
    const inputCantidad = document.getElementById('input-cantidad');
    const btnAgregar = document.getElementById('btn-agregar-adicional');
    const tablaBody = document.getElementById('tbody-adicionales');
    const campoHiddenJson = document.getElementById('adicionales_hidden_field');
    
    let listaAdicionales = [];

    function actualizarTablaAdicionales() {
        if (!tablaBody) return;
        tablaBody.innerHTML = '';
        let subtotalAdicionales = 0;

        listaAdicionales.forEach((item, index) => {
            const subtotalItem = parseFloat(item.precio) * parseInt(item.cantidad);
            subtotalAdicionales += subtotalItem;

            const fila = `
                <tr>
                    <td>${item.nombre}</td>
                    <td>${item.cantidad}</td>
                    <td>S/ ${subtotalItem.toFixed(2)}</td>
                    <td class="text-end">
                        <button type="button" class="btn btn-danger btn-sm btn-eliminar-adicional" data-index="${index}">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </td>
                </tr>
            `;
            tablaBody.innerHTML += fila;
        });

        if (campoHiddenJson) {
            campoHiddenJson.value = JSON.stringify(listaAdicionales);
        }
        
        // ¡Llama al calculador principal cada vez que la tabla cambia!
        calcularTotalReserva();
    }

    if (btnAgregar) {
        btnAgregar.addEventListener('click', function() {
            // ... (lógica para agregar, se queda igual) ...
            const selectedOption = selectAdicional.options[selectAdicional.selectedIndex];
            const id = selectedOption.value;
            const cantidad = parseInt(inputCantidad.value);

            if (!id || cantidad <= 0) {
                alert('Por favor, selecciona un adicional y una cantidad válida.');
                return;
            }
            const nombre = selectedOption.getAttribute('data-nombre');
            const precio = parseFloat(selectedOption.getAttribute('data-precio'));
            const itemExistente = listaAdicionales.find(item => item.id === id);
            
            if (itemExistente) {
                itemExistente.cantidad += cantidad;
            } else {
                listaAdicionales.push({ id, nombre, precio, cantidad });
            }
            actualizarTablaAdicionales();
            selectAdicional.selectedIndex = 0;
            inputCantidad.value = 1;
        });
    }

    if (tablaBody) {
        tablaBody.addEventListener('click', function(event) {
            // ... (lógica para eliminar, se queda igual) ...
            const botonEliminar = event.target.closest('.btn-eliminar-adicional');
            if (botonEliminar) {
                const indexAEliminar = parseInt(botonEliminar.getAttribute('data-index'));
                listaAdicionales.splice(indexAEliminar, 1);
                actualizarTablaAdicionales();
            }
        });
    }

    // ================================================================
    // === PARTE 2: LÓGICA DE "FORMULARIO DINÁMICO"
    // ================================================================
    
    // --- 1. Seleccionar los elementos ---
    const modal = document.getElementById('modalNuevaReserva');
    const grupoModalidad = document.getElementById('modalidad-group');
    const grupoSalon = document.getElementById('salon-column-container');
    const grupoHorario = document.getElementById('horario-group');
    const grupoPaquete = document.getElementById('paquete-group');
    const selectHorario = document.getElementById('horario'); 
    const selectPaquete = document.getElementById('paquete'); 
    const inputNinos = document.getElementById('input_ninos');
    const inputAdultos = document.getElementById('input_adultos');
    
    // --- ¡NUEVO! ---
    // Selecciona el campo de Total que movimos al footer
    const campoTotal = document.getElementById('campo_total_reserva');
    
    // Variable global para guardar los datos de la API
    let opcionesReserva = {};

    // --- 2. Función para poblar (llenar) los <select> ---
    function poblarSelect(selectElement, opciones) {
        if (!selectElement) return;
        selectElement.innerHTML = '';
        selectElement.add(new Option('-- Seleccionar --', ''));
        opciones.forEach(op => {
            selectElement.add(new Option(op.texto, op.id));
        });
    }

    // --- 3. Nueva Función para actualizar mínimos de Niños/Adultos ---
    function actualizarMinimos(minimos) {
        if (!inputNinos || !inputAdultos) return;
        const minNinos = minimos.ninos;
        const minAdultos = minimos.adultos;

        inputNinos.min = minNinos;
        inputAdultos.min = minAdultos;
        if (inputNinos.value === "0" || parseInt(inputNinos.value) < minNinos) inputNinos.value = minNinos;
        if (inputAdultos.value === "0" || parseInt(inputAdultos.value) < minAdultos) inputAdultos.value = minAdultos;
        inputNinos.placeholder = `Mín. ${minNinos}`;
        inputAdultos.placeholder = `Mín. ${minAdultos}`;
    }

    // --- 4. ¡NUEVO! EL CALCULADOR PRINCIPAL ---
    function calcularTotalReserva() {
        if (!campoTotal || !opcionesReserva.precios_paquete) return; // Salir si no está listo

        let precioBase = 0;
        let totalAdicionales = 0;
        
        // Obtener valores actuales
        const modalidadSeleccionada = document.querySelector('input[name="modalidad"]:checked')?.value;
        const numNinos = parseInt(inputNinos.value) || 0;
        const numAdultos = parseInt(inputAdultos.value) || 0;

        // 1. Calcular Precio Base
        if (modalidadSeleccionada) {
            const precioPaquete = opcionesReserva.precios_paquete[modalidadSeleccionada] || 0;
            
            if (modalidadSeleccionada === 'Exclusivo') {
                precioBase = precioPaquete; // Es el precio fijo: 3200
            } else {
                // Es un paquete: (Niños * Precio) + (Adultos * 5)
                const totalNinos = numNinos * precioPaquete;
                const totalAdultos = numAdultos * 5; // Precio fijo por adulto
                precioBase = totalNinos + totalAdultos;
            }
        }
        
        // 2. Calcular Total Adicionales
        listaAdicionales.forEach(item => {
            totalAdicionales += parseFloat(item.precio) * parseInt(item.cantidad);
        });

        // 3. Sumar y mostrar
        const granTotal = precioBase + totalAdicionales;
        campoTotal.value = granTotal.toFixed(2);
    }

    // --- 5. Cargamos los datos y adjuntamos listeners ---
    fetch('/api/opciones-reserva')
        .then(response => response.json())
        .then(data => {
            opcionesReserva = data; // Guardar datos globalmente
            
            // --- 6. ESCUCHAR CAMBIOS en MODALIDAD ---
            if (grupoModalidad) {
                grupoModalidad.addEventListener('change', function(e) {
                    if (e.target.name === 'modalidad') {
                        const modalidadElegida = e.target.value;
                        let minimos = {ninos: 0, adultos: 0};

                        if (modalidadElegida === 'Exclusivo') {
                            minimos = opcionesReserva.minimos['Exclusivo'];
                            grupoSalon.style.display = 'none';
                            grupoPaquete.style.display = 'none';
                            grupoHorario.style.display = 'block';
                            const opcionExclusiva = [{"id": "9:00 AM - 1:00 PM", "texto": "9:00 AM - 1:00 PM"}];
                            poblarSelect(selectHorario, opcionExclusiva);
                            selectHorario.value = "9:00 AM - 1:00 PM";
                            selectHorario.disabled = true;
                        } else {
                            // Resetear a 0, se establecerá al elegir salón
                            minimos = {ninos: 0, adultos: 0}; 
                            grupoSalon.style.display = 'block';
                            grupoHorario.style.display = 'none';
                            grupoPaquete.style.display = 'none';
                            selectHorario.disabled = false;
                            if (selectHorario) selectHorario.innerHTML = '';
                            
                            if (opcionesReserva.paquetes && opcionesReserva.paquetes[modalidadElegida]) {
                                poblarSelect(selectPaquete, opcionesReserva.paquetes[modalidadElegida]);
                            } else {
                                if (selectPaquete) selectPaquete.innerHTML = '';
                            }
                        }
                        
                        actualizarMinimos(minimos);
                        calcularTotalReserva(); // ¡Actualizar total!
                        const radiosSalon = grupoSalon.querySelectorAll('input[type="radio"]');
                        radiosSalon.forEach(radio => radio.checked = false);
                    }
                });
            }

            // --- 7. ESCUCHAR CAMBIOS en SALÓN ---
            if (grupoSalon) {
                grupoSalon.addEventListener('change', function(e) {
                    if (e.target.name === 'salon') {
                        const salonElegido = e.target.value;
                        grupoHorario.style.display = 'block';
                        grupoPaquete.style.display = 'block';

                        const minimos = opcionesReserva.minimos[salonElegido];
                        if (minimos) actualizarMinimos(minimos);
                        
                        if (opcionesReserva.horarios && opcionesReserva.horarios[salonElegido]) {
                            poblarSelect(selectHorario, opcionesReserva.horarios[salonElegido]);
                        } else {
                            if (selectHorario) selectHorario.innerHTML = '';
                        }
                        
                        calcularTotalReserva(); // ¡Actualizar total!
                    }
                });
            }

            // --- 8. ESCUCHAR CAMBIOS en NIÑOS y ADULTOS ---
            if(inputNinos) inputNinos.addEventListener('change', calcularTotalReserva);
            if(inputAdultos) inputAdultos.addEventListener('change', calcularTotalReserva);

            // --- 9. Limpiar modal al cerrar ---
            if (modal) {
                modal.addEventListener('hidden.bs.modal', function () {
                    // ... (tu lógica de limpieza) ...
                    document.getElementById('form-nueva-reserva').reset();
                    grupoSalon.style.display = 'none';
                    grupoHorario.style.display = 'none';
                    grupoPaquete.style.display = 'none';
                    listaAdicionales = [];
                    actualizarTablaAdicionales(); // Esto llamará a calcularTotalReserva
                    calcularTotalReserva(); // Asegura un reseteo final
                });
            }
        })
        .catch(error => console.error('Error al cargar opciones de reserva:', error));
});