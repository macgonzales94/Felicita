package com.felicita.felicita.controller;

import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.service.EmpleadoService;
import com.felicita.felicita.service.ReservaService;
import com.felicita.felicita.service.ServicioService;
import com.felicita.felicita.service.UsuarioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;
import java.util.Optional;

/**
 * Controlador para las vistas relacionadas con reservas.
 */
@Controller
@RequestMapping("/reservas")
public class ReservaViewController {

    @Autowired
    private ReservaService reservaService;
    
    @Autowired
    private UsuarioService usuarioService;
    
    @Autowired
    private ServicioService servicioService;
    
    @Autowired
    private EmpleadoService empleadoService;

    /**
     * Muestra el formulario para crear una nueva reserva
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/nueva")
    public String nuevaReserva(Model model) {
        List<Servicio> servicios = servicioService.obtenerTodosActivos();
        List<Empleado> empleados = empleadoService.obtenerTodosActivos();
        
        model.addAttribute("servicios", servicios);
        model.addAttribute("empleados", empleados);
        
        return "reservas/nueva";
    }

    /**
     * Muestra las reservas del usuario actual
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/mis-reservas")
    public String misReservas(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            Usuario usuario = usuarioOpt.get();
            List<Reserva> reservas = reservaService.buscarPorUsuario(usuario.getId());
            model.addAttribute("reservas", reservas);
        }
        
        return "reservas/mis-reservas";
    }

    /**
     * Muestra los detalles de una reserva
     * @param id ID de la reserva
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/{id}")
    public String detallesReserva(@PathVariable Long id, Model model) {
        Optional<Reserva> reservaOpt = reservaService.obtenerPorId(id);
        
        if (reservaOpt.isPresent()) {
            Reserva reserva = reservaOpt.get();
            List<Servicio> servicios = reservaService.obtenerServiciosPorReserva(id);
            
            model.addAttribute("reserva", reserva);
            model.addAttribute("servicios", servicios);
            
            return "reservas/detalles";
        } else {
            return "redirect:/reservas/mis-reservas";
        }
    }

    /**
     * Muestra la página de confirmación después de crear una reserva
     * @param id ID de la reserva
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/{id}/confirmacion")
    public String confirmacionReserva(@PathVariable Long id, Model model) {
        Optional<Reserva> reservaOpt = reservaService.obtenerPorId(id);
        
        if (reservaOpt.isPresent()) {
            Reserva reserva = reservaOpt.get();
            List<Servicio> servicios = reservaService.obtenerServiciosPorReserva(id);
            
            model.addAttribute("reserva", reserva);
            model.addAttribute("servicios", servicios);
            
            return "reservas/confirmacion";
        } else {
            return "redirect:/reservas/mis-reservas";
        }
    }
}