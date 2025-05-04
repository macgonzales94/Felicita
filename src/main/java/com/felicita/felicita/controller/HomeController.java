package com.felicita.felicita.controller;

import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.service.ServicioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import jakarta.servlet.http.HttpServletRequest;

import java.util.List;

/**
 * Controlador para la página principal y otras páginas públicas.
 */
@Controller
public class HomeController {

    @Autowired
    private ServicioService servicioService;

    /**
     * Muestra la página principal
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/")
    public String inicio(HttpServletRequest request, Model model) {
        List<Servicio> serviciosDestacados = servicioService.obtenerTodosActivos();
        model.addAttribute("servicios", serviciosDestacados);
        model.addAttribute("httpServletRequest", request);
        return "home";
    }

    /**
     * Muestra la página de servicios
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/servicios")
    public String servicios(HttpServletRequest request, Model model) {
        List<Servicio> servicios = servicioService.obtenerTodosActivos();
        model.addAttribute("servicios", servicios);
        model.addAttribute("httpServletRequest", request);
        return "servicios";
    }

    /**
     * Muestra la página de contacto
     * @return Nombre de la vista
     */
    @GetMapping("/contacto")
    public String contacto(HttpServletRequest request, Model model) {
        model.addAttribute("httpServletRequest", request);
        return "contacto";
    }

    /**
     * Muestra la página "Acerca de nosotros"
     * @return Nombre de la vista
     */
    @GetMapping("/nosotros")
    public String nosotros(HttpServletRequest request, Model model) {
        model.addAttribute("httpServletRequest", request);
        return "nosotros";
    }
}