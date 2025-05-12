package com.felicita.felicita.controller;

import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.Testimonio;
import com.felicita.felicita.service.EmpleadoService;
import com.felicita.felicita.service.ServicioService;
import com.felicita.felicita.service.TestimonioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Controlador para gestionar las páginas principales públicas del sistema FELICITA.
 * Se encarga de manejar las rutas de acceso público como la página principal,
 * servicios, contacto, y páginas informativas.
 */
@Controller
public class HomeController {

    @Autowired
    private ServicioService servicioService;
    
    @Autowired
    private EmpleadoService empleadoService;
    
    @Autowired
    private TestimonioService testimonioService;

    /**
     * Muestra la página principal
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/")
    public String index(Model model) {
        try {
            // Servicios destacados
            List<Servicio> serviciosDestacados = new ArrayList<>();
            try {
                List<Servicio> todosLosServicios = servicioService.obtenerTodosActivos();
                // Limitamos a máximo 6 servicios para mostrar en la página principal
                serviciosDestacados = todosLosServicios.stream()
                    .limit(6)
                    .collect(Collectors.toList());
            } catch (Exception e) {
                // Log del error pero continuar con una lista vacía
                System.err.println("Error al cargar servicios: " + e.getMessage());
            }
            model.addAttribute("servicios", serviciosDestacados);
            
            // Profesionales destacados
            List<Empleado> profesionalesDestacados = new ArrayList<>();
            try {
                profesionalesDestacados = empleadoService.obtenerTodosActivos().stream()
                    .limit(3)
                    .collect(Collectors.toList());
            } catch (Exception e) {
                System.err.println("Error al cargar profesionales: " + e.getMessage());
            }
            model.addAttribute("profesionales", profesionalesDestacados);
            
            // Testimonios de clientes
            List<Testimonio> testimonios = new ArrayList<>();
            try {
                testimonios = testimonioService.obtenerTestimoniosDestacados();
            } catch (Exception e) {
                System.err.println("Error al cargar testimonios: " + e.getMessage());
            }
            model.addAttribute("testimonios", testimonios);
            
            // Estadísticas
            model.addAttribute("totalClientes", 500);
            model.addAttribute("totalServicios", 30);
            model.addAttribute("totalReservas", 1500);
            
            return "home";
        } catch (Exception e) {
            // Log del error
            System.err.println("Error al cargar la página principal: " + e.getMessage());
            e.printStackTrace();
            // En caso de error, devuelve una página de error genérica
            return "error";
        }
    }

    /**
     * Muestra la página principal (alias para /)
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/home")
    public String home(Model model) {
        return index(model);
    }

    /**
     * Muestra la página de servicios
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/servicios")
    public String servicios(Model model) {
        try {
            // Obtener todas las categorías para el filtro
            List<String> categorias = servicioService.obtenerCategorias();
            model.addAttribute("categorias", categorias);
            System.out.println("Categorías: " + categorias);
            
            // Obtener todos los servicios activos
            List<Servicio> servicios = servicioService.obtenerTodosActivos();
            System.out.println("Total servicios encontrados: " + servicios.size());
            model.addAttribute("servicios", servicios);
            
            // Obtener servicios más populares
            List<Servicio> serviciosPopulares = servicioService.obtenerServiciosMasPopulares(5);
            System.out.println("Servicios populares encontrados: " + serviciosPopulares.size());
            model.addAttribute("serviciosPopulares", serviciosPopulares);
            
            return "servicios";
        } catch (Exception e) {
            System.err.println("Error en servicios(): " + e.getMessage());
            e.printStackTrace();
            return "error";
        }
    }

    /**
     * Muestra la página de contacto
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/contacto")
    public String contacto(Model model) {
        // Añadimos un objeto de formulario vacío para el formulario de contacto
        model.addAttribute("contactForm", new ContactForm());
        
        // Información de contacto
        model.addAttribute("direccion", "Av. Arequipa 1234, Lima");
        model.addAttribute("telefono", "+51 987 654 321");
        model.addAttribute("email", "info@felicita.pe");
        model.addAttribute("horario", "Lun-Sáb: 9:00 - 19:00");
        
        // Coordenadas para el mapa (si se implementa)
        model.addAttribute("latitud", "-12.046374");
        model.addAttribute("longitud", "-77.042793");
        
        return "contacto";
    }
    
    /**
     * Procesa el formulario de contacto
     * @param contactForm Datos del formulario
     * @param redirectAttributes Para mensajes flash
     * @return Redirección a la página de contacto
     */
    @PostMapping("/contacto")
    public String procesarContacto(@ModelAttribute ContactForm contactForm, 
                                  RedirectAttributes redirectAttributes) {
        try {
            // Aquí iría la lógica para enviar el correo electrónico
            // o guardar el mensaje en la base de datos
            
            // Mensaje de éxito
            redirectAttributes.addFlashAttribute("mensajeExito", 
                "Tu mensaje ha sido enviado correctamente. Nos pondremos en contacto pronto.");
            
            return "redirect:/contacto";
        } catch (Exception e) {
            // Mensaje de error
            redirectAttributes.addFlashAttribute("mensajeError", 
                "Hubo un problema al enviar tu mensaje. Por favor, intenta nuevamente.");
            
            return "redirect:/contacto";
        }
    }

    /**
     * Muestra la página "Acerca de nosotros"
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/nosotros")
    public String nosotros(Model model) {
        // Historia de la empresa
        model.addAttribute("anioFundacion", "2022");
        model.addAttribute("historia", "FELICITA nació con la visión de transformar la forma en que las personas acceden a servicios de belleza...");
        
        // Valores
        List<String> valores = new ArrayList<>();
        valores.add("Excelencia");
        valores.add("Innovación");
        valores.add("Compromiso");
        valores.add("Integridad");
        model.addAttribute("valores", valores);
        
        // Equipo
        List<Empleado> equipoDirectivo = empleadoService.obtenerPorCargo("Directivo");
        model.addAttribute("equipoDirectivo", equipoDirectivo);
        
        return "nosotros";
    }
    
    /**
     * Muestra la página de términos y condiciones
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/terminos")
    public String terminos() {
        return "terminos";
    }
    
    /**
     * Muestra la página de política de privacidad
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/privacidad")
    public String privacidad() {
        return "privacidad";
    }
    
    /**
     * Muestra la página de preguntas frecuentes
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/faq")
    public String faq(Model model) {
        // Lista de preguntas frecuentes
        List<FaqItem> preguntas = new ArrayList<>();
        preguntas.add(new FaqItem(
            "¿Cómo puedo cancelar mi reserva?",
            "Puedes cancelar tu reserva hasta 24 horas antes sin penalidad desde tu perfil en 'Mis Reservas'."
        ));
        preguntas.add(new FaqItem(
            "¿Qué pasa si llego tarde a mi cita?",
            "Te recomendamos llegar 5-10 minutos antes. Si llegas hasta 15 minutos tarde, podemos atenderte pero con tiempo reducido."
        ));
        preguntas.add(new FaqItem(
            "¿Cómo puedo pagar mis servicios?",
            "Aceptamos pagos en efectivo, tarjetas de crédito/débito y transferencias bancarias."
        ));
        
        model.addAttribute("preguntasFrecuentes", preguntas);
        
        return "faq";
    }
    
    /**
     * Clase interna para los elementos de preguntas frecuentes
     */
    public static class FaqItem {
        private String pregunta;
        private String respuesta;
        
        public FaqItem(String pregunta, String respuesta) {
            this.pregunta = pregunta;
            this.respuesta = respuesta;
        }
        
        public String getPregunta() {
            return pregunta;
        }
        
        public String getRespuesta() {
            return respuesta;
        }
    }
    
    /**
     * Clase interna para el formulario de contacto
     */
    public static class ContactForm {
        private String nombre;
        private String email;
        private String telefono;
        private String asunto;
        private String mensaje;
        
        // Getters y setters
        public String getNombre() {
            return nombre;
        }
        
        public void setNombre(String nombre) {
            this.nombre = nombre;
        }
        
        public String getEmail() {
            return email;
        }
        
        public void setEmail(String email) {
            this.email = email;
        }
        
        public String getTelefono() {
            return telefono;
        }
        
        public void setTelefono(String telefono) {
            this.telefono = telefono;
        }
        
        public String getAsunto() {
            return asunto;
        }
        
        public void setAsunto(String asunto) {
            this.asunto = asunto;
        }
        
        public String getMensaje() {
            return mensaje;
        }
        
        public void setMensaje(String mensaje) {
            this.mensaje = mensaje;
        }
    }
}