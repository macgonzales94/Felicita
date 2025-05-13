package com.felicita.felicita.controller;

import com.felicita.felicita.model.*;
import com.felicita.felicita.service.*;
import com.felicita.felicita.dto.MensajeResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;
import java.util.Map;
import java.util.HashMap;
import java.util.Comparator;
import java.math.BigDecimal;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Controlador para el panel de administración de negocios (ProAdmin).
 * Gestiona las vistas y operaciones relacionadas con la administración de un salón de belleza o barbería.
 */
@Controller
@RequestMapping("/negocio")
@PreAuthorize("hasRole('PROADMIN')")
public class ProAdminController {

    @Autowired
    private UsuarioService usuarioService;
    
    @Autowired
    private NegocioService negocioService;
    
    @Autowired
    private EmpleadoService empleadoService;
    
    @Autowired
    private ServicioService servicioService;
    
    @Autowired
    private ReservaService reservaService;
    
    @Autowired
    private CategoriaService categoriaService;
    
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Muestra el dashboard principal del negocio
     */
    @GetMapping
    public String dashboard(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.findByUsername(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            Usuario usuario = usuarioOpt.get();
            Optional<Negocio> negocioOpt = negocioService.obtenerPorUsuario(usuario.getId());
            
            if (negocioOpt.isPresent()) {
                Negocio negocio = negocioOpt.get();
                model.addAttribute("negocio", negocio);
                
                // Obtener estadísticas y datos para el dashboard
                
                // Contar empleados
                List<Empleado> empleados = empleadoService.obtenerPorNegocio(negocio.getId());
                long empleadosActivos = empleados.stream()
                    .filter(Empleado::isActivo)
                    .count();
                
                // Contar servicios
                List<Servicio> servicios = servicioService.obtenerPorNegocio(negocio.getId());
                long serviciosActivos = servicios.stream()
                    .filter(Servicio::isActivo)
                    .count();
                
                // Obtener reservas recientes
                List<Reserva> reservasRecientes = reservaService.obtenerReservasRecientesPorNegocio(negocio, 5);
                
                // Calcular ingresos del mes actual
                LocalDateTime inicioMes = LocalDateTime.of(LocalDate.now().withDayOfMonth(1), LocalTime.MIN);
                LocalDateTime finMes = LocalDateTime.now();
                BigDecimal ingresosMes = reservaService.calcularIngresosPorPeriodo(negocio, inicioMes, finMes);
                
                // Obtener estadísticas de reservas por estado
                Map<Reserva.EstadoReserva, Long> estadisticasReservas = obtenerEstadisticasReservas(negocio);
                
                // Añadir atributos al modelo
                model.addAttribute("totalEmpleados", empleados.size());
                model.addAttribute("empleadosActivos", empleadosActivos);
                model.addAttribute("totalServicios", servicios.size());
                model.addAttribute("serviciosActivos", serviciosActivos);
                model.addAttribute("reservasRecientes", reservasRecientes);
                model.addAttribute("ingresosMes", ingresosMes);
                model.addAttribute("estadisticasReservas", estadisticasReservas);
                
                return "proadmin/dashboard";
            }
        }
        
        // Si no se encuentra el negocio o el usuario, redirigir a una página de error
        return "redirect:/error";
    }
    
    /**
     * Muestra la sección de gestión de servicios del negocio
     */
    @GetMapping("/servicios")
    public String servicios(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            model.addAttribute("negocio", negocio);
            
            // Obtener todos los servicios del negocio
            List<Servicio> servicios = servicioService.obtenerPorNegocio(negocio.getId());
            model.addAttribute("servicios", servicios);
            
            // Obtener categorías para el formulario de nuevo servicio
            List<Categoria> categorias = categoriaService.obtenerTodasActivasOrdenadas();
            model.addAttribute("categorias", categorias);
            
            // Añadir objeto para nuevo servicio
            model.addAttribute("nuevoServicio", new Servicio());
            
            return "proadmin/servicios";
        }
        
        return "redirect:/error";
    }
    
    /**
     * Procesa la creación de un nuevo servicio
     */
    @PostMapping("/servicios/crear")
    public String crearServicio(@AuthenticationPrincipal UserDetails userDetails, 
                               @ModelAttribute Servicio servicio,
                               RedirectAttributes redirectAttributes) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            
            // Asignar el negocio al servicio
            servicio.setNegocio(negocio);
            servicio.setActivo(true);
            
            // Guardar el servicio
            Servicio servicioCreado = servicioService.crearServicio(servicio);
            
            redirectAttributes.addFlashAttribute("mensajeExito", 
                "Servicio '" + servicioCreado.getNombre() + "' creado exitosamente");
            
            return "redirect:/negocio/servicios";
        }
        
        redirectAttributes.addFlashAttribute("mensajeError", "Error al crear el servicio. Negocio no encontrado.");
        return "redirect:/negocio/servicios";
    }
    
    /**
     * Muestra la página para editar un servicio
     */
    @GetMapping("/servicios/{id}/editar")
    public String editarServicio(@PathVariable Long id, 
                                @AuthenticationPrincipal UserDetails userDetails,
                                Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            model.addAttribute("negocio", negocio);
            
            // Verificar que el servicio exista y pertenezca al negocio
            Optional<Servicio> servicioOpt = servicioService.obtenerPorId(id);
            
            if (servicioOpt.isPresent() && servicioOpt.get().getNegocio().getId().equals(negocio.getId())) {
                model.addAttribute("servicio", servicioOpt.get());
                
                // Obtener categorías
                List<Categoria> categorias = categoriaService.obtenerTodasActivasOrdenadas();
                model.addAttribute("categorias", categorias);
                
                return "proadmin/servicio-editar";
            }
        }
        
        return "redirect:/negocio/servicios";
    }
    
    /**
     * Gestión de empleados del negocio
    */
    @GetMapping("/empleados")
    public String empleados(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            model.addAttribute("negocio", negocio);
            
            // Obtener todos los empleados del negocio
            List<Empleado> empleados = empleadoService.obtenerPorNegocio(negocio.getId());
            model.addAttribute("empleados", empleados);
            
            // Añadir objeto para nuevo empleado
            model.addAttribute("nuevoEmpleado", new Empleado());
            
            return "proadmin/empleados";
        }
        
        return "redirect:/error";
    }
    
    /**
     * Procesa la creación de un nuevo empleado
     */
    @PostMapping("/empleados/crear")
    public String crearEmpleado(@AuthenticationPrincipal UserDetails userDetails, 
                               @ModelAttribute Empleado empleado,
                               RedirectAttributes redirectAttributes) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            
            // Asignar el negocio al empleado
            empleado.setNegocio(negocio);
            empleado.setActivo(true);
            
            // Guardar el empleado
            Empleado empleadoCreado = empleadoService.crearEmpleado(empleado);
            
            redirectAttributes.addFlashAttribute("mensajeExito", 
                "Empleado '" + empleadoCreado.getNombre() + "' creado exitosamente");
            
            return "redirect:/negocio/empleados";
        }
        
        redirectAttributes.addFlashAttribute("mensajeError", "Error al crear el empleado. Negocio no encontrado.");
        return "redirect:/negocio/empleados";
    }
    
    /**
     * Gestión de reservas del negocio
    */
    @GetMapping("/reservas")
    public String reservas(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            model.addAttribute("negocio", negocio);
            
            // Obtener reservas del negocio
            List<Reserva> reservas = reservaService.obtenerPorNegocio(negocio);
            model.addAttribute("reservas", reservas);
            
            // Obtener empleados para el filtro
            List<Empleado> empleados = empleadoService.obtenerPorNegocio(negocio.getId());
            model.addAttribute("empleados", empleados);
            
            return "proadmin/reservas";
        }
        
        return "redirect:/error";
    }
        
    /**
     * Ver detalles de una reserva
     */
    @GetMapping("/reservas/{id}")
    public String detalleReserva(@PathVariable Long id,
                               @AuthenticationPrincipal UserDetails userDetails,
                               Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            
            // Obtener la reserva
            Optional<Reserva> reservaOpt = reservaService.obtenerPorId(id);
            
            // Verificar que la reserva pertenece al negocio
            if (reservaOpt.isPresent() && 
                reservaOpt.get().getEmpleado().getNegocio().getId().equals(negocio.getId())) {
                
                Reserva reserva = reservaOpt.get();
                model.addAttribute("reserva", reserva);
                
                // Obtener servicios de la reserva
                List<Servicio> servicios = reserva.getServiciosReservas().stream()
                    .map(ServicioReserva::getServicio)
                    .collect(Collectors.toList());
                model.addAttribute("servicios", servicios);
                
                return "proadmin/reserva-detalles";
            }
        }
        
        return "redirect:/negocio/reservas";
    }
    
    /**
     * Cambiar estado de una reserva
     */
    @PostMapping("/reservas/{id}/estado")
    public String cambiarEstadoReserva(@PathVariable Long id,
                                      @RequestParam Reserva.EstadoReserva nuevoEstado,
                                      @RequestParam(required = false) String motivoCancelacion,
                                      @AuthenticationPrincipal UserDetails userDetails,
                                      RedirectAttributes redirectAttributes) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            
            // Obtener la reserva
            Optional<Reserva> reservaOpt = reservaService.obtenerPorId(id);
            
            // Verificar que la reserva pertenece al negocio
            if (reservaOpt.isPresent() && 
                reservaOpt.get().getEmpleado().getNegocio().getId().equals(negocio.getId())) {
                
                Reserva reserva = reservaOpt.get();
                reserva.setEstado(nuevoEstado);
                
                // Si se está cancelando, guardar el motivo
                if (nuevoEstado == Reserva.EstadoReserva.CANCELADA && motivoCancelacion != null) {
                    reserva.setNotas(motivoCancelacion);
                }
                
                // Guardar los cambios
                reservaService.actualizar(reserva);
                
                redirectAttributes.addFlashAttribute("mensajeExito", 
                    "Estado de reserva actualizado a " + nuevoEstado);
            } else {
                redirectAttributes.addFlashAttribute("mensajeError", 
                    "Reserva no encontrada o no pertenece a este negocio");
            }
        } else {
            redirectAttributes.addFlashAttribute("mensajeError", "Negocio no encontrado");
        }
        
        return "redirect:/negocio/reservas/" + id;
    }
    
    /**
     * Configuración del negocio
     */
    @GetMapping("/configuracion")
    public String configuracion(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            model.addAttribute("negocio", negocio);
            
            // Convertir horarios y redes sociales de JSON a objetos, si existen
            try {
                if (negocio.getHorarioOperacion() != null && !negocio.getHorarioOperacion().isEmpty()) {
                    Map<String, Object> horarios = objectMapper.readValue(negocio.getHorarioOperacion(), Map.class);
                    model.addAttribute("horarios", horarios);
                }
                
                if (negocio.getRedesSociales() != null && !negocio.getRedesSociales().isEmpty()) {
                    Map<String, String> redesSociales = objectMapper.readValue(negocio.getRedesSociales(), Map.class);
                    model.addAttribute("redesSociales", redesSociales);
                }
            } catch (Exception e) {
                System.err.println("Error al procesar JSON: " + e.getMessage());
            }
            
            return "proadmin/configuracion";
        }
        
        return "redirect:/error";
    }
    
    /**
     * Actualiza la información del negocio
     */
    @PostMapping("/configuracion/actualizar")
    public String actualizarConfiguracion(@ModelAttribute Negocio negocioForm,
                                        @RequestParam Map<String, String> formParams,
                                        @AuthenticationPrincipal UserDetails userDetails,
                                        RedirectAttributes redirectAttributes) {
        Optional<Negocio> negocioOpt = obtenerNegocioActual(userDetails);
        
        if (negocioOpt.isPresent()) {
            Negocio negocio = negocioOpt.get();
            
            // Copiar propiedades básicas
            negocio.setNombreComercial(negocioForm.getNombreComercial());
            negocio.setDescripcion(negocioForm.getDescripcion());
            negocio.setDireccion(negocioForm.getDireccion());
            negocio.setTelefono(negocioForm.getTelefono());
            negocio.setCorreoContacto(negocioForm.getCorreoContacto());
            negocio.setTipo(negocioForm.getTipo());
            negocio.setLogo(negocioForm.getLogo());
            negocio.setSitioWeb(negocioForm.getSitioWeb());
            negocio.setLatitud(negocioForm.getLatitud());
            negocio.setLongitud(negocioForm.getLongitud());
            
            // Procesar horarios
            try {
                Map<String, Map<String, String>> horarios = new HashMap<>();
                String[] dias = {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"};
                
                for (String dia : dias) {
                    String desde = formParams.get("horario[" + dia + "].desde");
                    String hasta = formParams.get("horario[" + dia + "].hasta");
                    
                    if (desde != null && hasta != null) {
                        Map<String, String> horarioDia = new HashMap<>();
                        horarioDia.put("desde", desde);
                        horarioDia.put("hasta", hasta);
                        horarios.put(dia, horarioDia);
                    }
                }
                
                negocio.setHorarioOperacion(objectMapper.writeValueAsString(horarios));
            } catch (Exception e) {
                System.err.println("Error al procesar horarios: " + e.getMessage());
            }
            
            // Procesar redes sociales
            try {
                Map<String, String> redesSociales = new HashMap<>();
                redesSociales.put("facebook", formParams.get("redes.facebook"));
                redesSociales.put("instagram", formParams.get("redes.instagram"));
                redesSociales.put("tiktok", formParams.get("redes.tiktok"));
                redesSociales.put("whatsapp", formParams.get("redes.whatsapp"));
                
                negocio.setRedesSociales(objectMapper.writeValueAsString(redesSociales));
            } catch (Exception e) {
                System.err.println("Error al procesar redes sociales: " + e.getMessage());
            }
            
            // Guardar cambios
            MensajeResponse respuesta = negocioService.actualizarNegocio(negocio.getId(), negocio);
            
            if (respuesta.isExito()) {
                redirectAttributes.addFlashAttribute("mensajeExito", respuesta.getMensaje());
            } else {
                redirectAttributes.addFlashAttribute("mensajeError", respuesta.getMensaje());
            }
        } else {
            redirectAttributes.addFlashAttribute("mensajeError", "Negocio no encontrado");
        }
        
        return "redirect:/negocio/configuracion";
    }
    
    /**
     * Método auxiliar para obtener estadísticas de reservas
     */
    private Map<Reserva.EstadoReserva, Long> obtenerEstadisticasReservas(Negocio negocio) {
        List<Reserva> reservas = reservaService.obtenerPorNegocio(negocio);
        
        return reservas.stream()
            .collect(Collectors.groupingBy(Reserva::getEstado, Collectors.counting()));
    }
    
    /**
     * Método auxiliar para obtener el negocio del usuario actual
     */
    private Optional<Negocio> obtenerNegocioActual(UserDetails userDetails) {
        Optional<Usuario> usuarioOpt = usuarioService.findByUsername(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            Usuario usuario = usuarioOpt.get();
            return negocioService.obtenerPorUsuario(usuario.getId());
        }
        
        return Optional.empty();
    }
}