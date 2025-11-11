// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const overlay = document.getElementById('overlay');
    const body = document.body;

    // Función para abrir/cerrar el sidebar
    function toggleSidebar() {
        body.classList.toggle('sidebar-open');
    }

    // 1. Añadir evento al botón de hamburguesa
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    // 2. Añadir evento al overlay (para cerrar el menú al tocar fuera)
    if (overlay) {
        overlay.addEventListener('click', toggleSidebar);
    }

});

