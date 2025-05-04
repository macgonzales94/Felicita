package com.felicita.felicita.controller;

import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.service.ServicioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

/**
 * Controlador para gestionar las páginas principales públicas del sistema FELICITA.
 * Se encarga de manejar las rutas de acceso público como la página principal,
 * servicios, contacto, y páginas informativas.
 */
@Controller
public class HomeController {

    @Autowired
    private ServicioService servicioService;

    /**
     * Muestra la página principal
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/")
    public String home(Model model) {
        try {
            List<Servicio> serviciosDestacados = servicioService.obtenerTodosActivos();
            model.addAttribute("servicios", serviciosDestacados);
            return "home";
        } catch (Exception e) {
            // Log del error
            System.err.println("Error al cargar la página principal: " + e.getMessage());
            e.printStackTrace();
            // En caso de error, devuelve una página de error genérica
            return "error/general";
        }
    }

    /**
     * Muestra la página de servicios
     * @param model Modelo para pasar datos a la vista
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/servicios")
    public String servicios(Model model) {
        try {
            List<Servicio> servicios = servicioService.obtenerTodosActivos();
            model.addAttribute("servicios", servicios);
            return "servicios";
        } catch (Exception e) {
            System.err.println("Error al cargar la página de servicios: " + e.getMessage());
            e.printStackTrace();
            return "error/general";
        }
    }

    /**
     * Muestra la página de contacto
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/contacto")
    public String contacto() {
        return "contacto";
    }

    /**
     * Muestra la página "Acerca de nosotros"
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/nosotros")
    public String nosotros() {
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
     * Maneja errores HTTP 404 (Página no encontrada)
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/error/404")
    public String error404() {
        return "error/404";
    }
    
    /**
     * Página de error genérica - Cambiado para evitar conflicto con BasicErrorController
     * @return Nombre de la plantilla Thymeleaf a renderizar
     */
    @GetMapping("/error/general")
    public String errorGeneral() {
        return "error/general";
    }
}