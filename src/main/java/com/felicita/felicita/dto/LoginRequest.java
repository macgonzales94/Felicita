package com.felicita.felicita.dto;

import javax.validation.constraints.NotBlank;

/**
 * Clase que representa una solicitud de inicio de sesión.
 * Contiene los datos necesarios para autenticar a un usuario.
 */
public class LoginRequest {
    /**
     * Nombre de usuario para iniciar sesión
     */
    @NotBlank(message = "El nombre de usuario es obligatorio")
    private String nombreUsuario;

    /**
     * Contraseña del usuario
     */
    @NotBlank(message = "La contraseña es obligatoria")
    private String contraseña;

    // Getters y setters
    public String getNombreUsuario() {
        return nombreUsuario;
    }

    public void setNombreUsuario(String nombreUsuario) {
        this.nombreUsuario = nombreUsuario;
    }

    public String getContraseña() {
        return contraseña;
    }

    public void setContraseña(String contraseña) {
        this.contraseña = contraseña;
    }
}