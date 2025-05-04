/**
 * home.js - JavaScript específico para la página principal de FELICITA
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animación de números para estadísticas
    const counterElements = document.querySelectorAll('.counter-number');
    
    if (counterElements.length > 0) {
        const options = {
            threshold: 0.5
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const countTo = parseInt(target.getAttribute('data-count'));
                    let count = 0;
                    const duration = 2000; // 2 segundos
                    const increment = countTo / (duration / 16); // 60 FPS
                    
                    function updateCount() {
                        count += increment;
                        if (count < countTo) {
                            target.textContent = Math.ceil(count);
                            requestAnimationFrame(updateCount);
                        } else {
                            target.textContent = countTo;
                        }
                    }
                    
                    updateCount();
                    observer.unobserve(target);
                }
            });
        }, options);
        
        counterElements.forEach(el => {
            observer.observe(el);
        });
    }
    
    // Animación para elementos que aparecen al hacer scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        const animOptions = {
            threshold: 0.1
        };
        
        const animObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', entry.target.dataset.animation || 'animate__fadeIn');
                    animObserver.unobserve(entry.target);
                }
            });
        }, animOptions);
        
        animatedElements.forEach(el => {
            animObserver.observe(el);
        });
    }
    
    // Carrusel de testimonios
    const testimonialsCarousel = document.getElementById('testimonials-carousel');
    if (testimonialsCarousel) {
        new bootstrap.Carousel(testimonialsCarousel, {
            interval: 5000,
            touch: true
        });
    }
    
    // Botón de reserva rápida
    const quickBookBtn = document.getElementById('quick-book-btn');
    if (quickBookBtn) {
        quickBookBtn.addEventListener('click', function() {
            // Comprobar si el usuario está autenticado
            const isAuthenticated = document.body.classList.contains('user-authenticated');
            
            if (isAuthenticated) {
                window.location.href = '/reservas/nueva';
            } else {
                // Mostrar modal de login o registro
                const loginModal = new bootstrap.Modal(document.getElementById('login-modal'));
                loginModal.show();
            }
        });
    }
    
    // Filtro de servicios destacados
    const serviceFilter = document.getElementById('service-filter');
    if (serviceFilter) {
        serviceFilter.addEventListener('change', function() {
            const category = this.value;
            const cards = document.querySelectorAll('.service-card');
            
            cards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.closest('.service-item').style.display = 'block';
                } else {
                    card.closest('.service-item').style.display = 'none';
                }
            });
        });
    }
    
    // Efecto parallax para la sección hero
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.pageYOffset;
            heroSection.style.backgroundPositionY = (scrollPosition * 0.5) + 'px';
        });
    }
    
    // Efecto de mecanografía para el subtítulo del hero
    const typedElement = document.querySelector('.typed-text');
    if (typedElement) {
        const typedStrings = typedElement.getAttribute('data-typed-strings').split(',');
        let currentStringIndex = 0;
        let currentCharIndex = 0;
        let isDeleting = false;
        let typingSpeed = 100;
        
        function typeEffect() {
            const currentString = typedStrings[currentStringIndex];
            
            if (isDeleting) {
                typedElement.textContent = currentString.substring(0, currentCharIndex - 1);
                currentCharIndex--;
                typingSpeed = 50;
            } else {
                typedElement.textContent = currentString.substring(0, currentCharIndex + 1);
                currentCharIndex++;
                typingSpeed = 150;
            }
            
            if (!isDeleting && currentCharIndex === currentString.length) {
                isDeleting = true;
                typingSpeed = 1500; // Pausa al final de la escritura
            } else if (isDeleting && currentCharIndex === 0) {
                isDeleting = false;
                currentStringIndex = (currentStringIndex + 1) % typedStrings.length;
                typingSpeed = 500; // Pausa antes de escribir el siguiente string
            }
            
            setTimeout(typeEffect, typingSpeed);
        }
        
        typeEffect();
    }
});