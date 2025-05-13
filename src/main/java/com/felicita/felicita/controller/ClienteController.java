package com.felicita.felicita.controller;

import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.service.ReservaService;
import com.felicita.felicita.service.UsuarioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;
import java.util.Optional;

/**
 * Controlador para el panel de cliente.
 */
@Controller
@RequestMapping("/mi-cuenta")
@PreAuthorize("hasRole('CLIENTE')")
public class ClienteController {

    @Autowired
    private UsuarioService usuarioService;
    
    @Autowired
    private ReservaService reservaService;

    /**
     * Muestra el dashboard del cliente
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping
    public String dashboard(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            Usuario usuario = usuarioOpt.get();
            
            // Obtener reservas del usuario
            List<Reserva> reservas = reservaService.buscarPorUsuario(usuario.getId());
            
            // Obtener últimas reservas
            List<Reserva> ultimasReservas = reservas.stream()
                .limit(5)
                .toList();
            
            // Contar reservas por estado
            long reservasPendientes = reservas.stream()
                .filter(r -> r.getEstado() == Reserva.EstadoReserva.PENDIENTE)
                .count();
                
            long reservasConfirmadas = reservas.stream()
                .filter(r -> r.getEstado() == Reserva.EstadoReserva.CONFIRMADA)
                .count();
                
            long reservasCompletadas = reservas.stream()
                .filter(r -> r.getEstado() == Reserva.EstadoReserva.COMPLETADA)
                .count();
                
            long reservasCanceladas = reservas.stream()
                .filter(r -> r.getEstado() == Reserva.EstadoReserva.CANCELADA)
                .count();
            
            // Añadir datos al modelo
            model.addAttribute("usuario", usuario);
            model.addAttribute("ultimasReservas", ultimasReservas);
            model.addAttribute("totalReservas", reservas.size());
            model.addAttribute("reservasPendientes", reservasPendientes);
            model.addAttribute("reservasConfirmadas", reservasConfirmadas);
            model.addAttribute("reservasCompletadas", reservasCompletadas);
            model.addAttribute("reservasCanceladas", reservasCanceladas);
        }
        
        return "cliente/dashboard";
    }
    
    /**
     * Muestra el perfil del cliente
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/perfil")
    public String perfil(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            model.addAttribute("usuario", usuarioOpt.get());
        }
        
        return "cliente/perfil";
    }
    
    /**
     * Muestra el historial de reservas del cliente
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/reservas")
    public String reservas(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            Usuario usuario = usuarioOpt.get();
            List<Reserva> reservas = reservaService.buscarPorUsuario(usuario.getId());
            model.addAttribute("reservas", reservas);
            model.addAttribute("usuario", usuario);
        }
        
        return "cliente/reservas";
    }
    
    /**
     * Muestra las reservas favoritas/guardadas del cliente
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/favoritos")
    public String favoritos(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            // Aquí iría la lógica para obtener servicios favoritos (a implementar)
            model.addAttribute("usuario", usuarioOpt.get());
        }
        
        return "cliente/favoritos";
    }
    
    /**
     * Muestra las reseñas y valoraciones del cliente
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/resenas")
    public String resenas(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            // Aquí iría la lógica para obtener reseñas del usuario (a implementar)
            model.addAttribute("usuario", usuarioOpt.get());
        }
        
        return "cliente/resenas";
    }
    
    /**
     * Muestra la página de configuración de la cuenta
     * @param userDetails Detalles del usuario autenticado
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/configuracion")
    public String configuracion(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Optional<Usuario> usuarioOpt = usuarioService.obtenerPorNombreUsuario(userDetails.getUsername());
        
        if (usuarioOpt.isPresent()) {
            model.addAttribute("usuario", usuarioOpt.get());
        }
        
        return "cliente/configuracion";
    }
}