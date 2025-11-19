document.addEventListener('DOMContentLoaded', function () {
    
    // 1. LÓGICA "VER ABONO"
    const modalVerAbono = document.getElementById('modalVerAbono');
    if (modalVerAbono) {
        modalVerAbono.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            
            // Extraer datos de los atributos data-*
            const codigo = button.getAttribute('data-codigo');
            const fecha = button.getAttribute('data-fecha');
            const metodo = button.getAttribute('data-metodo');
            const monto = button.getAttribute('data-monto');
            const ref = button.getAttribute('data-ref');
            const user = button.getAttribute('data-user');
            const comentarios = button.getAttribute('data-comentarios');

            // Llenar el modal
            document.getElementById('abono_monto').textContent = 'S/ ' + monto;
            document.getElementById('abono_codigo').textContent = codigo;
            document.getElementById('abono_fecha').textContent = fecha;
            document.getElementById('abono_metodo').textContent = metodo;
            document.getElementById('abono_ref').textContent = ref;
            document.getElementById('abono_user').textContent = user;
            document.getElementById('abono_comentarios').textContent = comentarios;
        });
    }

    // 2. LÓGICA "IR A RESERVA"
    // Esto reutiliza el modal de "Ver Reserva" que ya tienes en base.html
    document.body.addEventListener('click', function(e) {
        const btnIrReserva = e.target.closest('.btn-ir-reserva');
        if (btnIrReserva) {
            const reservaId = btnIrReserva.getAttribute('data-reserva-id');
            
            // Buscar el modal de Ver Reserva (que está en base.html)
            // Usamos bootstrap para abrirlo
            const modalReservaEl = document.getElementById('modalVerReserva');
            if (modalReservaEl) {
                // Necesitamos simular que el botón tenía los atributos necesarios
                // O mejor, disparamos el evento manualmente pasando el ID
                
                // Truco: Creamos un botón falso temporal para activar el modal
                // Esto aprovecha la lógica que ya escribiste en reservas.js
                const tempButton = document.createElement('button');
                tempButton.setAttribute('data-bs-toggle', 'modal');
                tempButton.setAttribute('data-bs-target', '#modalVerReserva');
                tempButton.setAttribute('data-id', reservaId);
                document.body.appendChild(tempButton);
                tempButton.click();
                document.body.removeChild(tempButton);
            }
        }
    });
});