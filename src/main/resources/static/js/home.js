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
                    // Obtener la animación del atributo data
                    const animation = entry.target.dataset.animation || 'animate__fadeIn';
                    
                    // Obtener el retraso si existe
                    const delay = entry.target.dataset.delay || 0;
                    
                    // Aplicar retraso si es necesario
                    if (delay > 0) {
                        setTimeout(() => {
                            entry.target.classList.add('animate__animated', animation);
                        }, delay);
                    } else {
                        entry.target.classList.add('animate__animated', animation);
                    }
                    
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
            interval: 5000,  // 5 segundos entre diapositivas
            touch: true,     // Permitir deslizamiento táctil
            pause: 'hover'   // Pausar al pasar el ratón
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
                if (loginModal) {
                    loginModal.show();
                } else {
                    // Si no hay modal, redireccionar al login
                    window.location.href = '/login?redirect=/reservas/nueva';
                }
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
                const cardCategory = card.dataset.category;
                const serviceItem = card.closest('.service-item');
                
                if (category === 'all' || cardCategory === category) {
                    if (serviceItem) {
                        serviceItem.style.display = 'block';
                    }
                } else {
                    if (serviceItem) {
                        serviceItem.style.display = 'none';
                    }
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
    
    // Botón Volver Arriba
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
    
    // Login Modal (si existe)
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        // Cambiar entre formularios de login y registro
        const loginForm = loginModal.querySelector('#login-form');
        const registerForm = loginModal.querySelector('#register-form');
        const switchToRegister = loginModal.querySelector('#switch-to-register');
        const switchToLogin = loginModal.querySelector('#switch-to-login');
        
        if (switchToRegister && loginForm && registerForm) {
            switchToRegister.addEventListener('click', function(e) {
                e.preventDefault();
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            });
        }
        
        if (switchToLogin && loginForm && registerForm) {
            switchToLogin.addEventListener('click', function(e) {
                e.preventDefault();
                registerForm.style.display = 'none';
                loginForm.style.display = 'block';
            });
        }
    }
});