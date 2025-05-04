package com.felicita.felicita.dto;

/**
 * Clase que representa la respuesta después de una autenticación exitosa.
 * Contiene el token JWT generado y su tipo.
 */
public class JwtResponse {
    /**
     * Token de acceso JWT
     */
    private String tokenAcceso;
    
    /**
     * Tipo de token (Bearer)
     */
    private String tipoToken = "Bearer";
    
    /**
     * Nombre de usuario autenticado
     */
    private String nombreUsuario;
    
    /**
     * Rol del usuario autenticado
     */
    private String rol;

    /**
     * Constructor con token de acceso
     */
    public JwtResponse(String tokenAcceso) {
        this.tokenAcceso = tokenAcceso;
    }

    /**
     * Constructor completo
     */
    public JwtResponse(String tokenAcceso, String nombreUsuario, String rol) {
        this.tokenAcceso = tokenAcceso;
        this.nombreUsuario = nombreUsuario;
        this.rol = rol;
    }

    // Getters
    public String getTokenAcceso() {
        return tokenAcceso;
    }

    public String getTipoToken() {
        return tipoToken;
    }
    
    public String getNombreUsuario() {
        return nombreUsuario;
    }
    
    public String getRol() {
        return rol;
    }
}