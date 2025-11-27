// Menú lateral expandible/colapsable
document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar (colapsar/expandir)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.querySelector('.main-wrapper');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainWrapper.classList.toggle('sidebar-collapsed');
            
            // Guardar estado en localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restaurar estado del sidebar
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            mainWrapper.classList.add('sidebar-collapsed');
        }
    }
    
    // Toggle secciones del menú
    const sectionToggles = document.querySelectorAll('[data-section-toggle]');
    sectionToggles.forEach(toggle => {
        // Colapsar todas las secciones por defecto (arrancar comprimido)
        const section = toggle.closest('.menu-section');
        if (section) {
            section.classList.add('collapsed');
            const content = section.querySelector('[data-section-content]');
            if (content) {
                content.classList.remove('expanded');
            }
            const arrow = toggle.querySelector('.menu-section-arrow');
            if (arrow) {
                arrow.style.transform = 'rotate(0deg)';
            }
        }
        
        toggle.addEventListener('click', function() {
            const section = this.closest('.menu-section');
            const content = section.querySelector('[data-section-content]');
            const arrow = this.querySelector('.menu-section-arrow');
            
            section.classList.toggle('collapsed');
            section.classList.toggle('expanded');
            if (content) {
                content.classList.toggle('expanded');
            }
            
            if (arrow) {
                arrow.style.transform = section.classList.contains('collapsed') 
                    ? 'rotate(0deg)' 
                    : 'rotate(90deg)';
            }
        });
    });
    
    // Toggle submenús
    const submenuToggles = document.querySelectorAll('[data-submenu-toggle]');
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const menuItem = this.closest('.menu-item');
            const submenu = menuItem.querySelector('[data-submenu-content]');
            const arrow = this.querySelector('.menu-arrow');
            
            menuItem.classList.toggle('expanded');
            submenu.classList.toggle('expanded');
            
            if (arrow) {
                arrow.style.transform = menuItem.classList.contains('expanded') 
                    ? 'rotate(90deg)' 
                    : 'rotate(0deg)';
            }
        });
    });
    
    // Marcar item activo basado en la URL actual
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.menu-link, .menu-sublink');
    
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            // Expandir secciones y submenús padre (solo la que contiene el item activo)
            let parent = link.closest('.menu-section, .menu-item');
            while (parent) {
                if (parent.classList.contains('menu-section')) {
                    parent.classList.remove('collapsed'); // Remover collapsed
                    parent.classList.add('expanded');
                    const content = parent.querySelector('[data-section-content]');
                    if (content) content.classList.add('expanded');
                    const arrow = parent.querySelector('.menu-section-arrow');
                    if (arrow) arrow.style.transform = 'rotate(90deg)';
                } else if (parent.classList.contains('menu-item')) {
                    parent.classList.add('expanded');
                    const submenu = parent.querySelector('[data-submenu-content]');
                    if (submenu) submenu.classList.add('expanded');
                    const arrow = parent.querySelector('.menu-arrow');
                    if (arrow) arrow.style.transform = 'rotate(90deg)';
                }
                parent = parent.parentElement.closest('.menu-section, .menu-item');
            }
        }
    });
});

