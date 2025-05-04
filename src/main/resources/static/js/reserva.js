/**
 * reserva.js - JavaScript específico para la página de reservas de FELICITA
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let currentStep = 1;
    const totalSteps = 3;
    let selectedServices = [];
    let selectedDate = null;
    let selectedTime = null;
    let selectedStylist = null;
    
    // Elementos DOM
    const stepContainers = document.querySelectorAll('.step-container');
    const stepIndicators = document.querySelectorAll('.step');
    const nextButtons = document.querySelectorAll('.btn-next');
    const prevButtons = document.querySelectorAll('.btn-prev');
    const serviceCards = document.querySelectorAll('.service-card');
    const calendarDays = document.querySelectorAll('.calendar-day');
    const timeSlots = document.querySelectorAll('.time-slot');
    const stylistCards = document.querySelectorAll('.stylist-card');
    const confirmBtn = document.getElementById('confirm-booking');
    
    // Resumen de reserva
    const summaryServicesList = document.getElementById('summary-services');
    const summaryDate = document.getElementById('summary-date');
    const summaryTime = document.getElementById('summary-time');
    const summaryStylist = document.getElementById('summary-stylist');
    const summaryTotal = document.getElementById('summary-total');
    
    // Inicialización
    initializeSteps();
    initializeServices();
    initializeCalendar();
    initializeTimeSlots();
    initializeStylists();
    
    /**
     * Inicializa la navegación entre pasos
     */
    function initializeSteps() {
        // Mostrar solo el primer paso al inicio
        showStep(currentStep);
        
        // Asignar eventos a botones de siguiente
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                if (validateCurrentStep()) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });
        
        // Asignar eventos a botones de anterior
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentStep--;
                showStep(currentStep);
            });
        });
        
        // Botón de confirmación final
        if (confirmBtn) {
            confirmBtn.addEventListener('click', confirmBooking);
        }
    }
    
    /**
     * Muestra el paso especificado y actualiza los indicadores
     */
    function showStep(step) {
        // Ocultar todos los contenedores de pasos
        stepContainers.forEach(container => {
            container.style.display = 'none';
        });
        
        // Mostrar el contenedor del paso actual
        if (stepContainers[step - 1]) {
            stepContainers[step - 1].style.display = 'block';
        }
        
        // Actualizar indicadores de pasos
        stepIndicators.forEach((indicator, index) => {
            if (index + 1 < step) {
                indicator.classList.remove('active');
                indicator.classList.add('completed');
                indicator.innerHTML = '<i class="fas fa-check"></i>';
            } else if (index + 1 === step) {
                indicator.classList.add('active');
                indicator.classList.remove('completed');
                indicator.textContent = index + 1;
            } else {
                indicator.classList.remove('active', 'completed');
                indicator.textContent = index + 1;
            }
        });
        
        // Actualizar el resumen en cada paso
        updateSummary();
        
        // Desplazarse al principio de la página
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    /**
     * Valida el paso actual antes de avanzar
     */
    function validateCurrentStep() {
        switch (currentStep) {
            case 1: // Selección de servicios
                if (selectedServices.length === 0) {
                    showAlert('Por favor, selecciona al menos un servicio', 'warning');
                    return false;
                }
                return true;
                
            case 2: // Selección de fecha y hora
                if (!selectedDate) {
                    showAlert('Por favor, selecciona una fecha', 'warning');
                    return false;
                }
                if (!selectedTime) {
                    showAlert('Por favor, selecciona un horario', 'warning');
                    return false;
                }
                return true;
                
            case 3: // Selección de estilista
                if (!selectedStylist) {
                    showAlert('Por favor, selecciona un profesional', 'warning');
                    return false;
                }
                return true;
                
            default:
                return true;
        }
    }
    
    /**
     * Inicializa la selección de servicios
     */
    function initializeServices() {
        serviceCards.forEach(card => {
            card.addEventListener('click', function() {
                this.classList.toggle('selected');
                
                const serviceId = parseInt(this.dataset.id);
                const serviceName = this.querySelector('.service-title').textContent;
                const servicePrice = parseFloat(this.dataset.price);
                const serviceDuration = parseInt(this.dataset.duration);
                
                if (this.classList.contains('selected')) {
                    // Agregar servicio
                    selectedServices.push({
                        id: serviceId,
                        name: serviceName,
                        price: servicePrice,
                        duration: serviceDuration
                    });
                } else {
                    // Eliminar servicio
                    selectedServices = selectedServices.filter(service => service.id !== serviceId);
                }
                
                updateSummary();
            });
        });
    }
    
    /**
     * Inicializa el calendario para selección de fecha
     */
    function initializeCalendar() {
        calendarDays.forEach(day => {
            if (!day.classList.contains('disabled')) {
                day.addEventListener('click', function() {
                    // Quitar selección anterior
                    calendarDays.forEach(d => d.classList.remove('selected'));
                    
                    // Seleccionar día actual
                    this.classList.add('selected');
                    selectedDate = this.dataset.date;
                    
                    // Actualizar horarios disponibles según fecha
                    updateAvailableTimeSlots(selectedDate);
                    
                    updateSummary();
                });
            }
        });
    }
    
    /**
     * Inicializa los horarios para selección
     */
    function initializeTimeSlots() {
        timeSlots.forEach(slot => {
            slot.addEventListener('click', function() {
                if (!this.classList.contains('disabled')) {
                    // Quitar selección anterior
                    timeSlots.forEach(s => s.classList.remove('selected'));
                    
                    // Seleccionar horario actual
                    this.classList.add('selected');
                    selectedTime = this.dataset.time;
                    
                    updateSummary();
                }
            });
        });
    }
    
    /**
     * Actualiza los horarios disponibles según fecha seleccionada
     */
    function updateAvailableTimeSlots(date) {
        // En una implementación real, aquí se haría una llamada AJAX para obtener los horarios disponibles
        // Por ahora, simulamos algunos horarios ocupados
        
        // Primero habilitamos todos
        timeSlots.forEach(slot => {
            slot.classList.remove('disabled');
        });
        
        // Luego deshabilitamos algunos aleatoriamente para simular
        const disabledTimes = [2, 5, 7]; // Índices que se deshabilitarán
        disabledTimes.forEach(index => {
            if (timeSlots[index]) {
                timeSlots[index].classList.add('disabled');
                
                // Si el slot deshabilitado estaba seleccionado, quitar selección
                if (timeSlots[index].classList.contains('selected')) {
                    timeSlots[index].classList.remove('selected');
                    selectedTime = null;
                }
            }
        });
    }
    
    /**
     * Inicializa la selección de estilistas
     */
    function initializeStylists() {
        stylistCards.forEach(card => {
            card.addEventListener('click', function() {
                // Quitar selección anterior
                stylistCards.forEach(c => c.classList.remove('selected'));
                
                // Seleccionar estilista actual
                this.classList.add('selected');
                selectedStylist = {
                    id: parseInt(this.dataset.id),
                    name: this.querySelector('.stylist-name').textContent
                };
                
                updateSummary();
            });
        });
    }
    
    /**
     * Actualiza el resumen de la reserva
     */
    function updateSummary() {
        // Actualizar lista de servicios
        if (summaryServicesList) {
            if (selectedServices.length === 0) {
                summaryServicesList.innerHTML = '<p class="text-muted">No has seleccionado servicios</p>';
            } else {
                let servicesHtml = '';
                let total = 0;
                
                selectedServices.forEach(service => {
                    servicesHtml += `
                        <div class="summary-item">
                            <span class="summary-label">${service.name}</span>
                            <span class="summary-value">S/. ${service.price.toFixed(2)}</span>
                        </div>
                    `;
                    total += service.price;
                });
                
                summaryServicesList.innerHTML = servicesHtml;
                
                if (summaryTotal) {
                    summaryTotal.textContent = `S/. ${total.toFixed(2)}`;
                }
            }
        }
        
        // Actualizar fecha
        if (summaryDate) {
            summaryDate.textContent = selectedDate ? formatDate(selectedDate) : '-';
        }
        
        // Actualizar hora
        if (summaryTime) {
            summaryTime.textContent = selectedTime || '-';
        }
        
        // Actualizar estilista
        if (summaryStylist) {
            summaryStylist.textContent = selectedStylist ? selectedStylist.name : '-';
        }
    }
    
    /**
     * Procesa la confirmación de la reserva
     */
    function confirmBooking() {
        if (validateCurrentStep()) {
            // Aquí se haría la llamada AJAX para guardar la reserva
            const bookingData = {
                services: selectedServices.map(s => s.id),
                date: selectedDate,
                time: selectedTime,
                stylistId: selectedStylist.id,
                notes: document.getElementById('booking-notes') ? document.getElementById('booking-notes').value : ''
            };
            
            console.log('Enviando datos de reserva:', bookingData);
            
            // Simular éxito
            showLoadingSpinner();
            
            setTimeout(() => {
                hideLoadingSpinner();
                
                // Redirigir a página de confirmación
                window.location.href = '/reservas/confirmacion?id=12345';
                
                // Alternativa: mostrar mensaje de éxito
                // showAlert('Reserva confirmada exitosamente!', 'success');
            }, 1500);
        }
    }
    
    /**
     * Muestra una alerta
     */
    function showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container') || createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto cerrar después de 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    }
    
    /**
     * Crea el contenedor de alertas si no existe
     */
    function createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    }
    
    /**
     * Muestra el spinner de carga
     */
    function showLoadingSpinner() {
        const spinnerContainer = document.createElement('div');
        spinnerContainer.id = 'loading-spinner';
        spinnerContainer.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        spinnerContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        spinnerContainer.style.zIndex = '2000';
        
        spinnerContainer.innerHTML = `
            <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Cargando...</span>
            </div>
        `;
        
        document.body.appendChild(spinnerContainer);
    }
    
    /**
     * Oculta el spinner de carga
     */
    function hideLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
    
    /**
     * Formatea una fecha en formato legible
     */
    function formatDate(dateString) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', options);
    }
    
    /**
     * Busca servicios según texto ingresado
     */
    const searchInput = document.getElementById('search-services');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchText = this.value.toLowerCase();
            
            serviceCards.forEach(card => {
                const serviceName = card.querySelector('.service-title').textContent.toLowerCase();
                const serviceDesc = card.querySelector('.service-description').textContent.toLowerCase();
                
                if (serviceName.includes(searchText) || serviceDesc.includes(searchText)) {
                    card.closest('.service-wrapper').style.display = 'block';
                } else {
                    card.closest('.service-wrapper').style.display = 'none';
                }
            });
        });
    }
    
    /**
     * Filtra servicios por categoría
     */
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const category = this.value;
            
            serviceCards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.closest('.service-wrapper').style.display = 'block';
                } else {
                    card.closest('.service-wrapper').style.display = 'none';
                }
            });
        });
    }
});