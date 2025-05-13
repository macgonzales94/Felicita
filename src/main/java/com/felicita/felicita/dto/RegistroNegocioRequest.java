package com.felicita.felicita.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Clase que representa una solicitud de registro de negocio.
 * Contiene los datos necesarios para crear un nuevo usuario tipo PROADMIN y su negocio.
 */
public class RegistroNegocioRequest {
    /**
     * Nombre de usuario para iniciar sesión
     */
    @NotBlank(message = "El nombre de usuario es obligatorio")
    @Size(min = 3, max = 20, message = "El nombre de usuario debe tener entre 3 y 20 caracteres")
    private String nombreUsuario;

    /**
     * Correo electrónico del usuario
     */
    @NotBlank(message = "El correo electrónico es obligatorio")
    @Size(max = 50, message = "El correo electrónico no debe exceder los 50 caracteres")
    @Email(message = "El formato del correo electrónico no es válido")
    private String correo;

    /**
     * Contraseña del usuario
     */
    @NotBlank(message = "La contraseña es obligatoria")
    @Size(min = 6, max = 40, message = "La contraseña debe tener entre 6 y 40 caracteres")
    private String contraseña;
    
    /**
     * Nombre completo del usuario
     */
    @NotBlank(message = "El nombre completo es obligatorio")
    private String nombreCompleto;
    
    /**
     * Número de teléfono del usuario
     */
    private String telefono;
    
    /**
     * Nombre comercial del negocio
     */
    @NotBlank(message = "El nombre comercial del negocio es obligatorio")
    private String nombreComercial;
    
    /**
     * Dirección del negocio
     */
    @NotBlank(message = "La dirección del negocio es obligatoria")
    private String direccion;
    
    /**
     * Tipo de negocio
     */
    @NotBlank(message = "El tipo de negocio es obligatorio")
    private String tipoNegocio;

    // Getters y setters
    public String getNombreUsuario() {
        return nombreUsuario;
    }

    public void setNombreUsuario(String nombreUsuario) {
        this.nombreUsuario = nombreUsuario;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public String getContraseña() {
        return contraseña;
    }

    public void setContraseña(String contraseña) {
        this.contraseña = contraseña;
    }

    public String getNombreCompleto() {
        return nombreCompleto;
    }

    public void setNombreCompleto(String nombreCompleto) {
        this.nombreCompleto = nombreCompleto;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }
    
    public String getNombreComercial() {
        return nombreComercial;
    }
    
    public void setNombreComercial(String nombreComercial) {
        this.nombreComercial = nombreComercial;
    }
    
    public String getDireccion() {
        return direccion;
    }
    
    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }
    
    public String getTipoNegocio() {
        return tipoNegocio;
    }
    
    public void setTipoNegocio(String tipoNegocio) {
        this.tipoNegocio = tipoNegocio;
    }
}