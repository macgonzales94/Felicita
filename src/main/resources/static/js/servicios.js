/**
 * servicios.js - JavaScript específico para la página de servicios de FELICITA
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    const categoryTabs = document.querySelectorAll('.category-tabs .nav-link, .categories-list a');
    const servicioCards = document.querySelectorAll('#contenedorServicios .service-card');
    const serviceBuscador = document.getElementById('serviceBuscador');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const filtroPrecio = document.getElementById('filtroPrecio');
    const noResultados = document.getElementById('noResultados');

    // Inicializar filtros
    initFilters();
    
    // Inicializar efectos de hover
    initHoverEffects();
    
    // Inicializar animaciones de entrada
    initAnimations();
    
    /**
     * Inicializa los eventos de filtrado
     */
    function initFilters() {
        // Filtro por categoría (pestañas)
        categoryTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remover clase activa de todas las pestañas
                document.querySelectorAll('.category-tabs .nav-link').forEach(t => t.classList.remove('active'));
                
                // Añadir clase activa a la pestaña correspondiente en el menú principal
                document.querySelector('.category-tabs .nav-link[data-categoria="' + this.getAttribute('data-categoria') + '"]').classList.add('active');
                
                // Filtrar servicios
                filtrarServicios();
            });
        });
        
        // Filtros de categoría y precio
        if (filtroCategoria) filtroCategoria.addEventListener('change', filtrarServicios);
        if (filtroPrecio) filtroPrecio.addEventListener('change', filtrarServicios);
        
        // Búsqueda de servicios
        if (serviceBuscador) {
            serviceBuscador.addEventListener('input', filtrarServicios);
            
            // Limpiar búsqueda con escape
            serviceBuscador.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    this.value = '';
                    filtrarServicios();
                }
            });
        }
    }
    
    /**
     * Filtra los servicios según los criterios seleccionados
     */
    function filtrarServicios() {
        const textoBusqueda = serviceBuscador ? serviceBuscador.value.toLowerCase() : '';
        const categoriaSeleccionada = document.querySelector('.category-tabs .nav-link.active').getAttribute('data-categoria');
        const categoriaFiltro = filtroCategoria ? filtroCategoria.value : 'todas';
        const precioFiltro = filtroPrecio ? filtroPrecio.value : 'todos';
        
        let hayResultados = false;
        
        servicioCards.forEach(servicio => {
            const nombre = servicio.querySelector('.card-title').textContent.toLowerCase();
            const descripcion = servicio.querySelector('.card-text').textContent.toLowerCase();
            const categoria = servicio.getAttribute('data-categoria');
            const precio = parseFloat(servicio.getAttribute('data-precio'));
            
            // Verificar filtro de texto
            const coincideTexto = nombre.includes(textoBusqueda) || descripcion.includes(textoBusqueda);
            
            // Verificar filtro de categoría por tab
            const coincideCategoriaPestaña = categoriaSeleccionada === 'todas' || categoria === categoriaSeleccionada;
            
            // Verificar filtro de categoría por select
            const coincideCategoriaSelect = categoriaFiltro === 'todas' || categoria === categoriaFiltro;
            
            // Verificar filtro de precio
            let coincidePrecio = true;
            if (precioFiltro === '0-50') {
                coincidePrecio = precio <= 50;
            } else if (precioFiltro === '50-100') {
                coincidePrecio = precio > 50 && precio <= 100;
            } else if (precioFiltro === '100-200') {
                coincidePrecio = precio > 100 && precio <= 200;
            } else if (precioFiltro === '200+') {
                coincidePrecio = precio > 200;
            }
            
            // Mostrar u ocultar servicio con una animación
            if (coincideTexto && coincideCategoriaPestaña && coincideCategoriaSelect && coincidePrecio) {
                if (servicio.style.display === 'none') {
                    fadeIn(servicio);
                } else {
                    servicio.style.display = 'block';
                }
                hayResultados = true;
            } else {
                fadeOut(servicio);
            }
        });
        
        // Mostrar mensaje si no hay resultados
        if (noResultados) {
            if (!hayResultados) {
                fadeIn(noResultados);
            } else {
                fadeOut(noResultados);
            }
        }
        
        // Actualizar contador de resultados
        actualizarContador(hayResultados ? countVisibleServices() : 0);
    }
    
    /**
     * Inicializa los efectos de hover en las tarjetas de servicio
     */
    function initHoverEffects() {
        servicioCards.forEach(card => {
            const imageContainer = card.querySelector('.service-image-container');
            const actions = card.querySelector('.service-actions');
            
            if (imageContainer && actions) {
                imageContainer.addEventListener('mouseenter', function() {
                    actions.style.bottom = '0';
                });
                
                imageContainer.addEventListener('mouseleave', function() {
                    actions.style.bottom = '-50px';
                });
            }
            
            // Añadir efecto de escala a la imagen
            const img = card.querySelector('img');
            if (img) {
                card.addEventListener('mouseenter', function() {
                    img.style.transform = 'scale(1.05)';
                });
                
                card.addEventListener('mouseleave', function() {
                    img.style.transform = 'scale(1)';
                });
            }
        });
    }
    
    /**
     * Inicializa las animaciones de entrada
     */
    function initAnimations() {
        // Animación de entrada para tarjetas
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                        entry.target.style.opacity = 1;
                    }, entry.target.dataset.delay || 0);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        // Añadir clases y delay de animación a cada tarjeta
        servicioCards.forEach((card, index) => {
            card.style.opacity = 0;
            card.dataset.delay = index * 100;
            observer.observe(card);
        });
    }
    
    /**
     * Anima la entrada de un elemento con efecto de fade
     * @param {HTMLElement} element - Elemento a animar
     */
    function fadeIn(element) {
        element.style.opacity = 0;
        element.style.display = 'block';
        
        let opacity = 0;
        const interval = setInterval(() => {
            opacity += 0.1;
            element.style.opacity = opacity;
            
            if (opacity >= 1) {
                clearInterval(interval);
            }
        }, 30);
    }
    
    /**
     * Anima la salida de un elemento con efecto de fade
     * @param {HTMLElement} element - Elemento a animar
     */
    function fadeOut(element) {
        let opacity = 1;
        const interval = setInterval(() => {
            opacity -= 0.1;
            element.style.opacity = opacity;
            
            if (opacity <= 0) {
                clearInterval(interval);
                element.style.display = 'none';
            }
        }, 30);
    }
    
    /**
     * Cuenta los servicios visibles
     * @returns {number} - Número de servicios visibles
     */
    function countVisibleServices() {
        return Array.from(servicioCards).filter(card => card.style.display !== 'none').length;
    }
    
    /**
     * Actualiza el contador de resultados
     * @param {number} count - Número de resultados
     */
    function actualizarContador(count) {
        const contador = document.getElementById('contadorResultados');
        if (contador) {
            contador.textContent = count;
            contador.parentElement.style.display = 'block';
        }
    }
    
    /**
     * Función para inicializar tooltips
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Inicializar tooltips si Bootstrap está cargado
    if (typeof bootstrap !== 'undefined') {
        initTooltips();
    }
    
    // Botón "Volver arriba"
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.opacity = '1';
                backToTopBtn.style.visibility = 'visible';
            } else {
                backToTopBtn.style.opacity = '0';
                backToTopBtn.style.visibility = 'hidden';
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
});