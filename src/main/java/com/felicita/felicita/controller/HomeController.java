package com.felicita.felicita.controller;

import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.service.ServicioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

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
    public String inicio(Model model) {
        try {
            List<Servicio> serviciosDestacados = servicioService.obtenerTodosActivos();
            model.addAttribute("servicios", serviciosDestacados);
        } catch (Exception e) {
            // Si hay error al cargar servicios, no detener el renderizado de la página
            model.addAttribute("servicios", List.of());
        }
        return "home";
    }

    /**
     * Muestra la página de servicios
     * @param model Modelo para la vista
     * @return Nombre de la vista
     */
    @GetMapping("/servicios")
    public String servicios(Model model) {
        try {
            List<Servicio> servicios = servicioService.obtenerTodosActivos();
            model.addAttribute("servicios", servicios);
        } catch (Exception e) {
            model.addAttribute("servicios", List.of());
        }
        return "servicios";
    }

    /**
     * Muestra la página de contacto
     * @return Nombre de la vista
     */
    @GetMapping("/contacto")
    public String contacto() {
        return "contacto";
    }

    /**
     * Muestra la página "Acerca de nosotros"
     * @return Nombre de la vista
     */
    @GetMapping("/nosotros")
    public String nosotros() {
        return "nosotros";
    }
    
    /**
     * Maneja errores 404
     * @return Nombre de la vista de error
     */
    @GetMapping("/error")
    public String error() {
        return "error";
    }
}