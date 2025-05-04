package com.felicita.felicita.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import jakarta.servlet.http.HttpServletRequest;

/**
 * Controlador que maneja las vistas relacionadas con la autenticación.
 */
@Controller
public class AutenticacionViewController {

    /**
     * Muestra la página de inicio de sesión
     * @return Nombre de la vista de inicio de sesión
     */
    @GetMapping("/login")
    public String mostrarPaginaLogin(HttpServletRequest request, Model model) {
        // Añadir el objeto request al modelo para que esté disponible en la vista
        model.addAttribute("httpServletRequest", request);
        return "login";
    }

    /**
     * Muestra la página de registro
     * @return Nombre de la vista de registro
     */
    @GetMapping("/registro")
    public String mostrarPaginaRegistro(HttpServletRequest request, Model model) {
        // Añadir el objeto request al modelo para que esté disponible en la vista
        model.addAttribute("httpServletRequest", request);
        return "registro";
    }
}