package com.felicita.felicita.dto;

/**
 * Clase que representa una respuesta genérica con un mensaje.
 * Útil para respuestas de éxito o error.
 */
public class MensajeResponse {
    /**
     * Mensaje a mostrar
     */
    private String mensaje;
    
    /**
     * Indica si la operación fue exitosa
     */
    private boolean exito;

    /**
     * Constructor por defecto
     */
    public MensajeResponse() {
    }

    /**
     * Constructor con mensaje
     */
    public MensajeResponse(String mensaje) {
        this.mensaje = mensaje;
    }

    /**
     * Constructor completo
     */
    public MensajeResponse(String mensaje, boolean exito) {
        this.mensaje = mensaje;
        this.exito = exito;
    }

    // Getters y setters
    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public boolean isExito() {
        return exito;
    }

    public void setExito(boolean exito) {
        this.exito = exito;
    }
}