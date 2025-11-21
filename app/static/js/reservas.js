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
    // === PARTE 3: LÓGICA DE "VER DETALLE" Y "IMPRIMIR"
    // ==========================================================
    
    const modalVer = document.getElementById('modalVerReserva');
    const btnImprimir = document.getElementById('btnImprimirContrato');
    let datosReservaActual = null; // Variable para guardar los datos cargados

    if (modalVer) {
        modalVer.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget; 
            const idReserva = button.getAttribute('data-id'); 

            // Limpiar
            document.getElementById('view_codigo').textContent = "Cargando...";
            document.getElementById('view_tabla_adicionales').innerHTML = '';
            datosReservaActual = null; // Resetear variable

            fetch(`/api/reservas/${idReserva}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) { alert(data.error); return; }

                    // Guardamos los datos para usarlos al imprimir
                    datosReservaActual = data;

                    // Llenar campos visuales del modal
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
                    console.error("Error:", err);
                    document.getElementById('view_codigo').textContent = "Error";
                });
        });
    }

    // --- LÓGICA DE IMPRESIÓN (REPLICA DE WIX) ---
    if (btnImprimir) {
        btnImprimir.addEventListener('click', function() {
            if (!datosReservaActual) return;

            const r = datosReservaActual;
            const logoUrl = "/static/images/logo.png"; // Usamos tu logo local

            // Construir Tabla Adicionales
            let tablaAdicionalesHTML = '';
            if (r.adicionales && r.adicionales.length > 0) {
                let filas = '';
                r.adicionales.forEach(ad => {
                    const montoItem = (parseFloat(ad.precio) * parseInt(ad.cantidad)).toFixed(2);
                    filas += `
                        <tr>
                            <td>${ad.nombre}</td>
                            <td>S/. ${parseFloat(ad.precio).toFixed(2)}</td>
                            <td>${ad.cantidad}</td>
                            <td>S/. ${montoItem}</td>
                        </tr>`;
                });

                tablaAdicionalesHTML = `
                    <h3 style="font-size: 14px; margin-top: 15px; margin-bottom: 5px;">ADICIONALES</h3>
                    <table border="1" cellpadding="4" cellspacing="0" style="width: 100%; text-align: left; border-collapse: collapse; font-size: 11px;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th>Nombre</th>
                                <th>Precio Unitario</th>
                                <th>Cantidad</th>
                                <th>Monto</th>
                            </tr>
                        </thead>
                        <tbody>${filas}</tbody>
                    </table>`;
            }

            // HTML COMPLETO CON TÉRMINOS
            const contenidoHTML = `
                <html>
                <head>
                    <title>Contrato ${r.codigo}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.2; color: #333; padding: 20px; max-width: 800px; margin: auto; }
                        .resaltado { background-color: yellow !important; -webkit-print-color-adjust: exact; padding: 2px; }
                        .texto-normal { text-align: justify; font-size: 12px; font-weight: normal; margin-bottom: 6px; }
                        .watermark {
                            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                            opacity: 0.2; width: 80%; z-index: -1; pointer-events: none;
                        }
                        h2 { margin: 5px 0; }
                        h3 { font-size: 16px; margin-top: 20px; margin-bottom: 10px; font-weight: bold; }
                        h4 { font-size: 14px; margin-top: 15px; margin-bottom: 5px; font-weight: bold; }
                        ul { list-style: none; padding: 0; display: flex; flex-wrap: wrap; }
                        li { width: 50%; margin-bottom: 5px; font-size: 13px; }
                        
                        @media print {
                            .resaltado { background-color: yellow !important; -webkit-print-color-adjust: exact; }
                            .page-break { page-break-after: always; }
                        }
                    </style>
                </head>
                <body>
                    <img class="watermark" src="${logoUrl}" alt="Marca de Agua">
                    
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; border-bottom: 2px solid #ddd; padding-bottom: 10px;">
                        <div style="text-align: center; font-size: 12px;">
                            <h2 style="margin: 0;">¡ES HORA DE JUGAR!</h2>
                            <p style="margin: 2px 0;">Telf.: 943779110</p>
                            <p style="margin: 2px 0;">Facebook: Lúdicus Park</p>
                            <p style="margin: 2px 0;">Instagram: ludicuspark.peru</p>
                        </div>
                        <div style="text-align: right;">
                            <h3 style="margin: 0; font-size: 16px;">CONTRATO ${r.modalidad.toUpperCase().replace('PAQUETE ', '')} - ${r.codigo}</h3>
                            <p style="margin: 2px 0; font-size: 14px;">${r.created_at}</p>
                        </div>
                    </div>

                    <ul>
                        <li><strong>Cliente:</strong> ${r.nombre_padres}</li>
                        <li><strong>DNI:</strong> ${r.dni}</li>
                        <li><strong>TELF.:</strong> ${r.telefono}</li>
                        <li><strong>Día:</strong> ${r.fecha}</li>
                        <li><strong>Salón:</strong> ${r.salon}</li>
                        <li><strong>Horario:</strong> ${r.horario}</li>
                        <li><strong>Invitados:</strong> ${r.ninos} niños, ${r.adultos} adultos</li>
                        <li><strong>Cumpleañero / Edad:</strong> ${r.nombre_cumpleanero}</li>
                        <li><strong>Combo:</strong> ${r.paquete}</li>
                        <li style="width: 100%;"><strong>Accesorios:</strong> ${r.accesorios}</li>
                        <li style="width: 100%;"><strong>Observaciones:</strong> ${r.comentarios}</li>
                    </ul>

                    <div style="display: flex; justify-content: space-between; font-size: 16px; margin: 10px 0; border-top: 1px solid #ccc; padding-top: 10px;">
                        <span><strong>Total:</strong> S/. ${r.total.toFixed(2)}</span>
                        <span><strong>A cuenta:</strong> S/. ${r.a_cuenta.toFixed(2)}</span>
                        <span><strong>Saldo:</strong> S/. ${r.saldo.toFixed(2)}</span>
                    </div>

                    ${tablaAdicionalesHTML}

                    <h3>TÉRMINOS</h3>
                    <div style="font-size: 12px; text-align: justify;">
                        <p style="margin-bottom: 6px;">1. El contrato es por el horario y la fecha específica. El precio convenido se cancelará con el 50% del paquete/ cantidad de niños al momento de la reserva y el 50% restante, el pago de adultos y adicionales una vez finalizada el evento. Los pagos serán vía transferencia bancaria a nuestra Cta. Cte. INTERBANK, mediante tarjeta de crédito, débito o efectivo en nuestras instalaciones.</p>
                        <p style="margin-bottom: 6px;">2. Lúdicus Park no se responsabiliza por lesiones causadas por mal uso o falta de precaución en las instalaciones.</p>
                        <p style="margin-bottom: 6px;">3. Una vez realizado el contrato en cantidad de niños- adulto y adicionales el monto total es el que se debe de reconocer al momento de la celebración. (Se puede mantener o aumentar la cantidad de invitados, más no disminuir).</p>
                        <p style="margin-bottom: 6px;">4. No está permitido el ingreso a nuestros juegos y/o zonas recreativas, con algún tipo de calzado, juguete, alimento, bebida, accesorios, animales, espuma, serpentina, instrumentos punzocortantes y cualquier otro objeto que ponga en riesgo la integridad física de las personas. El acceso es EXCLUSIVAMENTE CON EL USO DE MEDIAS ANTIDESLIZANTES.</p>
                        <p style="margin-bottom: 6px;">5. Está prohibido el consumo de cigarros, uso de vape y/u objetos que desprendan humo en las instalaciones del parque.</p>
                        <p class="resaltado" style="margin-bottom: 6px;">6. En caso exista decoración externa, se admite como máximo 2 personas (NO NIÑOS), prohibido el uso de grapas, tachuelas o accesorios puntiagudos que involucren un deterioro al mobiliario prestado o a la integridad de los asistentes. El ingreso de la decoración es 30 minutos antes de la hora de reserva, en caso exista mobiliario externo, el plazo máximo de retiro o desmontaje es de 10 minutos posterior a la hora de término de contrato. En el caso se omita alguna de estas indicaciones, la persona que reservó deberá asumir el pago de una PENALIDAD CORRESPONDIENTE.</p>
                        <p style="margin-bottom: 6px;">8. En el caso la persona que reserve, desee que su torta sea repartida dentro del establecimiento durante las horas de reserva, deberá de cancelar el servicio de corte correspondiente a s/25 nuevos soles. Dicho servicio incluye el corte de la torta por parte de la anfitriona y el menaje correspondiente a platos y cucharas, con una cantidad máxima de 33 unidades.</p>
                        <p style="margin-top: 10px; font-size: 14px;"><strong>IMPORTANTE: No se permite el ingreso de comida o bebida externa, ni objetos punzocortantes como cuchillos, espátulas, entre otros. Así mismo no se permite el ingreso de show, payasos, arlequines, muñecos/botargas, carritos snacks. Como también el ingreso de bocaditos artesanales (sándwich de pollo, empanadas, alfajores, mazamorra, gelatina, manzanas acarameladas, algodones de azúcar, parrillas, gaseosas, chicha, bebidas alcohólicas, entre otros).</strong></p>
                    </div>

                    <div class="page-break" style="page-break-after: always;"></div>

                    <h3>CONDICIONES</h3>
                    <h4>RESERVAS/PAGOS</h4>
                    <div style="font-size: 12px; text-align: justify;">
                        <p class="texto-normal">1. Se podrá reprogramar una fecha de cumpleaños/reserva con un mínimo de 3 semanas de anticipación y sujeto a disponibilidad.</p>
                        <p class="texto-normal">2. En el caso de anulación de una reserva, se cobrará una penalidad del 30% del total del monto contratado, por concepto de gastos administrativos y pérdida de prospectos clientes.</p>
                        <p class="resaltado texto-normal">3. El cliente deberá cumplir y respetar el horario de finalización contratado previamente, en caso se exceda del tiempo establecido, pagará una penalidad correspondiente a tiempo excedido.</p>
                        <p class="resaltado texto-normal">4. La cantidad de niños y adultos invitados por cada reserva deberán ser confirmados antes del día de reserva, especialmente en el paquete LUDI SUPER ESTRELLA, esta debe de confirmarse en su totalidad máximo 4 días antes del día de celebración.</p>
                    </div>

                    <h4>RESTRICCIONES</h4>
                    <div style="font-size: 12px; text-align: justify;">
                        <p class="texto-normal">1. A la reserva de cualquier paquete de cumpleaños el cliente deberá firmar un consentimiento informado y/o extensión de responsabilidad de LÚDICUS PARK.</p>
                        <p class="texto-normal">2. LÚDICUS PARK, no se responsabiliza por eventuales lesiones en las personas por el mal uso, falta de precaución y/o no acatar las indicaciones de nuestro personal.</p>
                        <p class="texto-normal">3. No están permitidos los siguientes productos: botellas de vidrio con agua y/o gaseosas, refrescos, bebidas alcohólicas, gelatina, mazamorra morada, algodón de azúcar, chupetes, manzana acaramelada, alimentos que tiñan y/o colorantes.</p>
                        <p class="texto-normal">4. Se encuentra prohibido el uso de pica pica (bolitas de poliestireno) ni papel picado en las piñatas, aerosoles, máquinas de algodón, velas volcánicas, máquinas de humo ni realizar trucos con fuegos.</p>
                        <p class="texto-normal">5. Prohibido el ingreso y uso de objetos punzocortantes (cuchillos, espátulas, navajas, cuter, entre otros). y/o armas dentro y a las afueras de nuestro establecimiento. Salvo excepciones se cuente con seguridad privada del cliente, se permite que miembros de seguridad salvaguarden, pero a las afueras de nuestro establecimiento, todo con previa comunicación.</p>
                        <p class="resaltado texto-normal">6. El uso de los juegos es exclusivo para niños de 1 hasta los 14 años de edad. Considerando que la zona #1 es solo para niños de 1 hasta los 5 años, y la zona #2 para niños de 6 hasta los 14 años (incluye la Nave Ludi, Vertical Rush, El Barco y Jump), el juego METLDOWN es exclusivo para niños de 8 hasta los 14 años. Se pide respetar correctamente dichas indicaciones para la seguridad de sus invitados. Mayores de 15 años, se consideran como precio de adultos en la entrada.</p>
                        <p class="texto-normal">7. Nuestros paquetes no incluyen servilletas, vasos, hielo.</p>
                    </div>

                    <p style="margin-top: 20px; font-size: 12px;"><strong>HABIENDO LEÍDO Y ACEPTADO LOS TÉRMINOS Y CONDICIONES DE RENTA, SE FIRMA EL PRESENTE CONTRATO.</strong></p>
                    
                    <div style="margin-top: 80px; text-align: center;">
                        <p>______________________________</p>
                        <p style="font-weight: bold;">CONTRATANTE</p>
                        <p>${r.nombre_padres}</p>
                        <p>DNI: ${r.dni}</p>
                    </div>
                </body>
                </html>
            `;

            // Usar el iframe oculto para imprimir
            const iframe = document.getElementById('iframeImpresion');
            const doc = iframe.contentWindow.document;
            doc.open();
            doc.write(contenidoHTML);
            doc.close();
            
            // Esperar un momento a que carguen estilos/imagenes e imprimir
            setTimeout(() => {
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            }, 500);
        });
    }

});
})