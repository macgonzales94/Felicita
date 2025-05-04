/**
 * main.js - JavaScript global para FELICITA
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Agregar clase 'active' a enlaces de navegación según la URL actual
    const currentLocation = location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Animación de scroll suave para anclas internas
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Botón de volver arriba
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });

        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Menú móvil
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarMenu = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarMenu) {
        document.addEventListener('click', function(e) {
            const isClickInsideNavbar = navbarToggler.contains(e.target) || navbarMenu.contains(e.target);
            
            if (!isClickInsideNavbar && navbarMenu.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    }

    // Contador de caracteres para campos textarea
    document.querySelectorAll('textarea[maxlength]').forEach(function(textarea) {
        const counter = document.createElement('div');
        counter.className = 'small text-muted text-end mt-1';
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        
        function updateCounter() {
            const maxLength = textarea.getAttribute('maxlength');
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength}/${maxLength}`;
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
});

/**
 * Muestra una notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 * @param {number} duration - Duración en milisegundos
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Crear contenedor si no existe
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Mostrar toast
    const toastElement = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    toastElement.show();
    
    // Eliminar del DOM después de ocultarse
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Formatea una fecha en formato local
 * @param {string} dateString - Fecha en formato ISO
 * @param {boolean} includeTime - Indica si se debe incluir la hora
 * @returns {string} - Fecha formateada
 */
function formatDate(dateString, includeTime = false) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('es-ES', options);
}

/**
 * Formatea un valor monetario
 * @param {number} amount - Cantidad a formatear
 * @returns {string} - Cantidad formateada con símbolo de moneda
 */
function formatCurrency(amount) {
    return 'S/. ' + parseFloat(amount).toFixed(2);
}