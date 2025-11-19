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
        
        listaAdicionales.forEach((item, index) => {
            const subtotalItem = parseFloat(item.precio) * parseInt(item.cantidad);

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
            const botonEliminar = event.target.closest('.btn-eliminar-adicional');
            if (botonEliminar) {
                const indexAEliminar = parseInt(botonEliminar.getAttribute('data-index'));
                listaAdicionales.splice(indexAEliminar, 1);
                actualizarTablaAdicionales();
            }
        });
    }

    // ================================================================
    // === PARTE 2: LÓGICA DE "FORMULARIO DINÁMICO" Y "CALCULADORA"
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
    const campoTotal = document.getElementById('campo_total_reserva');
    
    // Lógica Admin (Sedes)
    const selectSedeAdmin = document.getElementById('select_sede_admin');
    const displayCodigo = document.getElementById('display_codigo_reserva');

    if (selectSedeAdmin) {
        selectSedeAdmin.addEventListener('change', function() {
            const sedeId = this.value;
            displayCodigo.textContent = "...";
            displayCodigo.style.opacity = "0.5";
            fetch(`/api/proximo-codigo/${sedeId}`)
                .then(response => response.json())
                .then(data => {
                    displayCodigo.textContent = data.codigo;
                    displayCodigo.style.opacity = "1";
                })
                .catch(err => console.error(err));
        });
    }
    
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

    // --- 4. EL CALCULADOR PRINCIPAL ---
    function calcularTotalReserva() {
        if (!campoTotal || !opcionesReserva.precios_paquete) return; 

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
            opcionesReserva = data; 
            
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
            if(inputNinos) inputNinos.addEventListener('input', calcularTotalReserva); // Evento input para tiempo real
            if(inputAdultos) inputAdultos.addEventListener('input', calcularTotalReserva);

            // ==========================================================
            // === PARTE 4: LÓGICA DE EDICIÓN Y LIMPIEZA
            // ==========================================================
            
            const formReserva = document.getElementById('form-nueva-reserva');
            const tituloModal = document.getElementById('modalNuevaReservaLabel'); 
            const btnSubmit = formReserva ? formReserva.querySelector('input[type="submit"]') : null;
            
            // --- GUARDAR EL CÓDIGO "NUEVO" ORIGINAL ---
            // Guardamos el valor inicial (ej: TR00006) para poder restaurarlo
            // cuando el usuario quiera crear una reserva después de haber editado otra.
            const codigoDisplay = document.getElementById('display_codigo_reserva');
            const codigoNuevoOriginal = codigoDisplay ? codigoDisplay.textContent : "";

            // A. AL ABRIR COMO "NUEVO" (Limpiar y Restaurar)
            const btnNuevo = document.querySelector('[data-bs-target="#modalNuevaReserva"]');
            if (btnNuevo) {
                btnNuevo.addEventListener('click', function() {
                    // 1. Restaurar textos visuales
                    if(tituloModal) tituloModal.textContent = "Nueva Reserva";
                    if(btnSubmit) btnSubmit.value = "Reservar";
                    if(codigoDisplay) codigoDisplay.textContent = codigoNuevoOriginal; // <--- RESTAURAR CÓDIGO
                    
                    // 2. Configurar acción del formulario
                    formReserva.action = "/api/reservas/nueva";
                    
                    // 3. Limpiar todo
                    formReserva.reset();
                    grupoSalon.style.display = 'none';
                    grupoHorario.style.display = 'none';
                    grupoPaquete.style.display = 'none';
                    selectHorario.disabled = false;
                    
                    listaAdicionales = [];
                    actualizarTablaAdicionales();
                    calcularTotalReserva(); 
                });
            }

            // B. AL ABRIR COMO "EDITAR" (Llenar y Cambiar Título)
            document.body.addEventListener('click', function(e) {
                const btnEditar = e.target.closest('.btn-editar-reserva');
                
                if (btnEditar) {
                    const idReserva = btnEditar.getAttribute('data-id');
                    
                    // 1. Abrir el modal manualmente
                    const modalInstance = new bootstrap.Modal(modal);
                    modalInstance.show();

                    // 2. Cambiar textos y acción
                    if(tituloModal) tituloModal.textContent = "Editar Reserva"; // <--- CAMBIAR TÍTULO
                    if(btnSubmit) btnSubmit.value = "Guardar Cambios";
                    formReserva.action = `/api/reservas/editar/${idReserva}`; 

                    // 3. Cargar datos de la API
                    fetch(`/api/reservas/${idReserva}`)
                        .then(res => res.json())
                        .then(data => {
                            // 3.1 ACTUALIZAR EL CÓDIGO VISUAL (Ej: Poner TR00005)
                            if(codigoDisplay) codigoDisplay.textContent = data.codigo; 

                            // 4. Llenar campos simples
                            document.querySelector('[name="nombre_padres"]').value = data.nombre_padres;
                            document.querySelector('[name="correo"]').value = data.correo !== "-" ? data.correo : "";
                            document.querySelector('[name="telefono"]').value = data.telefono;
                            document.querySelector('[name="dni_padres"]').value = data.dni !== "-" ? data.dni : "";
                            document.querySelector('[name="nombre_cumpleanero"]').value = data.nombre_cumpleanero !== "-" ? data.nombre_cumpleanero : "";
                            
                            // Fecha
                            if(data.fecha && data.fecha !== "-") {
                                const parts = data.fecha.split('/');
                                document.querySelector('[name="fecha_celebracion"]').value = `${parts[2]}-${parts[1]}-${parts[0]}`;
                            }

                            document.querySelector('[name="ninos"]').value = data.ninos;
                            document.querySelector('[name="adultos"]').value = data.adultos;
                            document.querySelector('[name="estado"]').value = data.estado;
                            document.querySelector('[name="accesorios"]').value = data.accesorios !== "Ninguno" ? data.accesorios : "";
                            document.querySelector('[name="comentarios"]').value = data.comentarios !== "Ninguno" ? data.comentarios : "";

                            // 5. Llenar Radios (Modalidad y Salón)
                            const radioModalidad = document.querySelector(`input[name="modalidad"][value="${data.modalidad}"]`);
                            if (radioModalidad) {
                                radioModalidad.checked = true;
                                radioModalidad.dispatchEvent(new Event('change')); 
                            }

                            setTimeout(() => {
                                const radioSalon = document.querySelector(`input[name="salon"][value="${data.salon}"]`);
                                if (radioSalon) {
                                    radioSalon.checked = true;
                                    radioSalon.dispatchEvent(new Event('change'));
                                }
                                
                                // 6. Llenar Selects Dinámicos
                                setTimeout(() => {
                                    document.querySelector('[name="horario"]').value = data.horario;
                                    document.querySelector('[name="paquete"]').value = data.paquete;
                                    calcularTotalReserva();
                                }, 100);
                            }, 50);

                            // 7. Llenar Tabla de Adicionales
                            listaAdicionales = data.adicionales || [];
                            actualizarTablaAdicionales(); 
                        })
                        .catch(err => console.error(err));
                }
            });

    // ==========================================================
    // === PARTE 3: LÓGICA DE "VER DETALLE" (MODAL DE LECTURA)
    // ==========================================================
    
    const modalVer = document.getElementById('modalVerReserva');
    
    if (modalVer) {
        modalVer.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget; 
            const idReserva = button.getAttribute('data-id'); 

            document.getElementById('view_codigo').textContent = "Cargando...";
            document.getElementById('view_tabla_adicionales').innerHTML = '';

            fetch(`/api/reservas/${idReserva}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    document.getElementById('view_codigo').textContent = data.codigo;
                    document.getElementById('view_estado').textContent = data.estado;
                    
                    const badge = document.getElementById('view_estado');
                    badge.className = 'badge fs-6'; 
                    if(data.estado === 'Reservado') badge.classList.add('bg-warning', 'text-dark');
                    else if(data.estado === 'Abonado') badge.classList.add('bg-success');
                    else badge.classList.add('bg-danger');

                    document.getElementById('view_padres').textContent = data.nombre_padres;
                    document.getElementById('view_dni').textContent = data.dni;
                    document.getElementById('view_telefono').textContent = data.telefono;
                    document.getElementById('view_correo').textContent = data.correo;
                    
                    document.getElementById('view_cumple').textContent = data.nombre_cumpleanero;
                    document.getElementById('view_fecha').textContent = data.fecha;
                    document.getElementById('view_horario').textContent = data.horario;
                    document.getElementById('view_salon').textContent = data.salon;
                    document.getElementById('view_modalidad').textContent = data.modalidad;
                    document.getElementById('view_paquete').textContent = data.paquete;
                    
                    document.getElementById('view_ninos').textContent = data.ninos;
                    document.getElementById('view_adultos').textContent = data.adultos;
                    document.getElementById('view_total').textContent = 'S/ ' + data.total.toFixed(2);
                    document.getElementById('view_accesorios').textContent = data.accesorios;
                    document.getElementById('view_comentarios').textContent = data.comentarios;

                    const tbody = document.getElementById('view_tabla_adicionales');
                    if (data.adicionales && data.adicionales.length > 0) {
                        data.adicionales.forEach(item => {
                            const subtotal = parseFloat(item.precio) * parseInt(item.cantidad);
                            const row = `
                                <tr class="border-bottom">
                                    <td>${item.nombre} <small class="text-muted d-block">S/ ${parseFloat(item.precio).toFixed(2)} c/u</small></td>
                                    <td class="text-center">${item.cantidad}</td>
                                    <td class="text-end">S/ ${subtotal.toFixed(2)}</td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });
                    } else {
                        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted small py-3">Sin adicionales</td></tr>';
                    }
                })
                .catch(err => {
                    console.error("Error al cargar reserva:", err);
                    document.getElementById('view_codigo').textContent = "Error de carga";
                });
        });
    }
});
})