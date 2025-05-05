package com.felicita.felicita.controller;

import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.service.ServicioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.ArrayList;
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
    public String index(Model model) {
        try {
            // Para evitar errores en la fase inicial, usar una lista vacía si hay problemas con la base de datos
            List<Servicio> serviciosDestacados = new ArrayList<>();
            try {
                serviciosDestacados = servicioService.obtenerTodosActivos();
            } catch (Exception e) {
                // Log del error pero continuar con una lista vacía
                System.err.println("Error al cargar servicios: " + e.getMessage());
            }
            model.addAttribute("servicios", serviciosDestacados);
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
            List<Servicio> servicios = new ArrayList<>();
            try {
                servicios = servicioService.obtenerTodosActivos();
            } catch (Exception e) {
                System.err.println("Error al cargar servicios: " + e.getMessage());
            }
            model.addAttribute("servicios", servicios);
            return "servicios";
        } catch (Exception e) {
            System.err.println("Error al cargar la página de servicios: " + e.getMessage());
            e.printStackTrace();
            return "error";
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
}