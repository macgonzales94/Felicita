package com.felicita.felicita.controller;

import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.service.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Controlador para el panel de administración.
 */
@Controller
@RequestMapping("/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    @Autowired
    private UsuarioService usuarioService;
    
    @Autowired
    private ServicioService servicioService;
    
    @Autowired
    private EmpleadoService empleadoService;
    
    @Autowired
    private ReservaService reservaService;
    
    @Autowired
    private DashboardService dashboardService;

    /**
     * Muestra el dashboard administrativo
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping
    public String dashboard(Model model) {
        // Obtener estadísticas para el último mes
        LocalDateTime ahora = LocalDateTime.now();
        LocalDateTime haceMes = ahora.minusMonths(1);
        
        long totalReservas = dashboardService.obtenerTotalReservas(haceMes, ahora);
        long totalClientes = dashboardService.obtenerTotalClientes();
        long totalServiciosActivos = dashboardService.obtenerTotalServiciosActivos();
        BigDecimal ingresosTotales = dashboardService.calcularIngresosTotales(haceMes, ahora);
        
        // Obtener reservas recientes
        List<Reserva> reservasRecientes = dashboardService.obtenerReservasRecientes(5);
        
        // Obtener servicios populares
        Map<Servicio, Long> serviciosPopulares = dashboardService.obtenerServiciosPopulares(5);
        
        // Obtener distribución de estados
        Map<Reserva.EstadoReserva, Long> distribucionEstados = dashboardService.obtenerDistribucionEstados();
        
        // Obtener estadísticas por día de la semana
        Map<String, Long> reservasPorDia = dashboardService.obtenerReservasPorDiaSemana(4);
        
        model.addAttribute("totalReservas", totalReservas);
        model.addAttribute("totalClientes", totalClientes);
        model.addAttribute("totalServiciosActivos", totalServiciosActivos);
        model.addAttribute("ingresosTotales", ingresosTotales);
        model.addAttribute("reservasRecientes", reservasRecientes);
        model.addAttribute("serviciosPopulares", serviciosPopulares);
        model.addAttribute("distribucionEstados", distribucionEstados);
        model.addAttribute("reservasPorDia", reservasPorDia);
        
        return "admin/dashboard";
    }

    /**
     * Gestión de usuarios
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/usuarios")
    public String usuarios(Model model) {
        List<Usuario> usuarios = usuarioService.obtenerTodos();
        model.addAttribute("usuarios", usuarios);
        return "admin/usuarios";
    }

    /**
     * Gestión de servicios
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/servicios")
    public String servicios(Model model) {
        List<Servicio> servicios = servicioService.obtenerTodos();
        model.addAttribute("servicios", servicios);
        return "admin/servicios";
    }

    /**
     * Gestión de empleados
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/empleados")
    public String empleados(Model model) {
        List<Empleado> empleados = empleadoService.obtenerTodos();
        model.addAttribute("empleados", empleados);
        return "admin/empleados";
    }

    /**
     * Gestión de reservas
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/reservas")
    public String reservas(Model model) {
        List<Reserva> reservas = reservaService.obtenerTodas();
        model.addAttribute("reservas", reservas);
        return "admin/reservas";
    }

    /**
     * Detalles de una reserva
     * @param id ID de la reserva
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/reservas/{id}")
    public String detallesReserva(@PathVariable Long id, Model model) {
        Optional<Reserva> reservaOpt = reservaService.obtenerPorId(id);
        
        if (reservaOpt.isPresent()) {
            Reserva reserva = reservaOpt.get();
            List<Servicio> servicios = reservaService.obtenerServiciosPorReserva(id);
            
            model.addAttribute("reserva", reserva);
            model.addAttribute("servicios", servicios);
            
            return "admin/reserva-detalles";
        } else {
            return "redirect:/admin/reservas";
        }
    }
}