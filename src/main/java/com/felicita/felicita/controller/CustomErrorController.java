package com.felicita.felicita.controller;

import org.springframework.boot.web.servlet.error.ErrorController;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.http.HttpServletRequest;

@Controller
public class CustomErrorController implements ErrorController {

    @RequestMapping("/error")
    public String handleError(HttpServletRequest request, Model model) {
        Object status = request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
        
        if (status != null) {
            Integer statusCode = Integer.valueOf(status.toString());
            model.addAttribute("statusCode", statusCode);
            
            // Agregar mensaje de error si está disponible
            Object errorMessage = request.getAttribute(RequestDispatcher.ERROR_MESSAGE);
            if (errorMessage != null) {
                model.addAttribute("errorMessage", errorMessage.toString());
            }
            
            // Agregar información de depuración en desarrollo
            Object exception = request.getAttribute(RequestDispatcher.ERROR_EXCEPTION);
            if (exception != null) {
                model.addAttribute("exception", exception.toString());
                System.err.println("Error en la aplicación: " + exception.toString());
            }
        }
        
        return "error";
    }
}