document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Configuración inicial: Obtener todos los elementos
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.content-section');
    const pageTitle = document.getElementById('page-title');

    // 2. Función para cambiar de sección
    function navigateTo(sectionId) {
        // A. Ocultar todas las secciones
        sections.forEach(section => {
            section.classList.remove('active-section');
        });

        // B. Mostrar la sección seleccionada
        const targetSection = document.getElementById('section-' + sectionId);
        if (targetSection) {
            targetSection.classList.add('active-section');
        }

        // C. Quitar la clase 'active' de todos los botones del menú
        menuItems.forEach(item => {
            item.classList.remove('active');
        });

        // D. Poner la clase 'active' en el botón del menú correcto
        const activeMenuItem = document.querySelector(`.menu-item[data-section="${sectionId}"]`);
        if (activeMenuItem) {
            activeMenuItem.classList.add('active');
        }

        // E. Cambiar el título grande de arriba
        pageTitle.textContent = sectionId.charAt(0).toUpperCase() + sectionId.slice(1);
    }

    // 3. Escuchar los clics en el menú lateral
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault(); // Evita que la página recargue
            
            const sectionId = this.getAttribute('data-section');
            
            // Cambiar el hash de la URL (Esto soluciona tu problema)
            window.location.hash = sectionId;
            
            // Ejecutar la navegación
            navigateTo(sectionId);
        });
    });

    // 4. Cargar la sección correcta al recargar la página o entrar directo
    function loadInitialSection() {
        // Si hay un hash en la URL (ej: .../admin/#ventas)
        let hash = window.location.hash.substring(1); // Quitar el #
        
        // Si no hay hash, cargar Dashboard por defecto
        if (!hash) {
            hash = 'dashboard';
        }

        // Validar si existe esa sección, si no, poner Dashboard
        const targetSection = document.getElementById('section-' + hash);
        if (!targetSection) {
            hash = 'dashboard';
        }

        // Ejecutar la navegación inicial
        navigateTo(hash);
    }

    // Ejecutar al cargar la página
    loadInitialSection();

    // Escuchar cuando el usuario use los botones de "Atrás/Adelante" del navegador
    window.addEventListener('hashchange', function() {
        let hash = window.location.hash.substring(1);
        if (!hash) hash = 'dashboard';
        navigateTo(hash);
    });

    // 5. Mostrar la fecha actual
    function updateDate() {
        const dateElement = document.getElementById('current-date');
        const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
        const today = new Date();
        // Forzar español (para que salga "martes" y no "Tuesday")
        dateElement.textContent = today.toLocaleDateString('es-CL', options); 
    }
    updateDate();
});