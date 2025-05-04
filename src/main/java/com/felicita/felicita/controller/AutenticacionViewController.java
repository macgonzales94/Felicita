package com.felicita.felicita.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

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
    public String mostrarPaginaLogin() {
        return "login";
    }

    /**
     * Muestra la página de registro
     * @return Nombre de la vista de registro
     */
    @GetMapping("/registro")
    public String mostrarPaginaRegistro() {
        return "registro";
    }
}