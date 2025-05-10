/**
 * contacto.js - JavaScript específico para la página de contacto de FELICITA
 */

document.addEventListener('DOMContentLoaded', function() {
    // Validación del formulario
    const form = document.getElementById('contactForm');
    
    if (form) {
        // Validar campos en tiempo real
        const inputElements = form.querySelectorAll('input, textarea');
        inputElements.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
        
        // Validar al enviar
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            // Validar todos los campos
            inputElements.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
                
                // Scroll al primer campo con error
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    firstInvalid.focus();
                }
            } else {
                // Mostrar spinner en envío
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
                    
                    // Restaurar botón después de 2 segundos (simulación)
                    // En producción, esto se manejaría con el evento de retorno del formulario
                    setTimeout(function() {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }, 2000);
                }
            }
        });
    }
    
    // Inicialización del mapa
    const mapaDiv = document.getElementById('mapa');
    
    if (mapaDiv) {
        const latitud = parseFloat(mapaDiv.getAttribute('data-latitud')) || -12.046374;
        const longitud = parseFloat(mapaDiv.getAttribute('data-longitud')) || -77.042793;
        
        const mapa = L.map('mapa').setView([latitud, longitud], 15);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(mapa);
        
        // Añadir marcador personalizado
        const iconoFelicita = L.icon({
            iconUrl: '/images/marker-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        });
        
        const marker = L.marker([latitud, longitud], {icon: iconoFelicita}).addTo(mapa);
        
        // Popup personalizado
        const popupContent = `
            <div class="map-popup">
                <h5 class="mb-1">FELICITA</h5>
                <p class="mb-1">Av. Arequipa 1234, Lima</p>
                <p class="mb-0"><i class="fas fa-phone-alt me-1"></i> +51 987 654 321</p>
            </div>
        `;
        
        marker.bindPopup(popupContent).openPopup();
        
        // Recalcular tamaño del mapa cuando la ventana cambia de tamaño
        window.addEventListener('resize', function() {
            mapa.invalidateSize();
        });
    }
    
    // Función para validar campos individuales
    function validateField(field) {
        // Remover estados anteriores
        field.classList.remove('is-valid', 'is-invalid');
        
        // Validar si el campo es requerido
        if (field.hasAttribute('required') && !field.value.trim()) {
            field.classList.add('is-invalid');
            return false;
        }
        
        // Validar email
        if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(field.value)) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        // Validar teléfono (opcional)
        if (field.id === 'telefono' && field.value.trim()) {
            const phoneRegex = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
            if (!phoneRegex.test(field.value)) {
                field.classList.add('is-invalid');
                return false;
            }
        }
        
        // Si pasó todas las validaciones
        if (field.value.trim()) {
            field.classList.add('is-valid');
        }
        
        return true;
    }
});