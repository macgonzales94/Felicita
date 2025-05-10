package com.felicita.felicita.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

/**
 * Clase que representa los testimonios de clientes del sistema.
 * Almacena opiniones y valoraciones sobre los servicios recibidos.
 */
@Entity
@Table(name = "testimonios")
public class Testimonio {
    /**
     * Identificador único del testimonio
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre del cliente que da el testimonio
     */
    @NotBlank
    @Size(max = 100)
    @Column(name = "nombre_cliente")
    private String nombreCliente;

    /**
     * Usuario asociado al testimonio (opcional)
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_usuario")
    private Usuario usuario;

    /**
     * Contenido del testimonio
     */
    @NotBlank
    @Size(max = 500)
    @Column(name = "mensaje")
    private String mensaje;

    /**
     * Valoración del cliente (1-5 estrellas)
     */
    @Min(1)
    @Max(5)
    @Column(name = "valoracion")
    private Integer valoracion;

    /**
     * Fecha en que se realizó el testimonio
     */
    @Column(name = "fecha")
    private LocalDateTime fecha;

    /**
     * Indica si el testimonio está aprobado para mostrar
     */
    @Column(name = "activo")
    private boolean activo = false;
    
    /**
     * Servicio asociado al testimonio (opcional)
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_servicio")
    private Servicio servicio;
    
    /**
     * Cargo o profesión del cliente (opcional)
     */
    @Size(max = 100)
    @Column(name = "cargo_cliente")
    private String cargoCliente;
    
    /**
     * URL de imagen del cliente (opcional)
     */
    @Size(max = 255)
    @Column(name = "imagen_cliente")
    private String imagenCliente;

    /**
     * Constructor por defecto
     */
    public Testimonio() {
        this.fecha = LocalDateTime.now();
    }

    /**
     * Constructor con parámetros principales
     */
    public Testimonio(String nombreCliente, String mensaje, Integer valoracion) {
        this.nombreCliente = nombreCliente;
        this.mensaje = mensaje;
        this.valoracion = valoracion;
        this.fecha = LocalDateTime.now();
    }

    // Getters y setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombreCliente() {
        return nombreCliente;
    }

    public void setNombreCliente(String nombreCliente) {
        this.nombreCliente = nombreCliente;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public void setUsuario(Usuario usuario) {
        this.usuario = usuario;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public Integer getValoracion() {
        return valoracion;
    }

    public void setValoracion(Integer valoracion) {
        this.valoracion = valoracion;
    }

    public LocalDateTime getFecha() {
        return fecha;
    }

    public void setFecha(LocalDateTime fecha) {
        this.fecha = fecha;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public Servicio getServicio() {
        return servicio;
    }

    public void setServicio(Servicio servicio) {
        this.servicio = servicio;
    }

    public String getCargoCliente() {
        return cargoCliente;
    }

    public void setCargoCliente(String cargoCliente) {
        this.cargoCliente = cargoCliente;
    }

    public String getImagenCliente() {
        return imagenCliente;
    }

    public void setImagenCliente(String imagenCliente) {
        this.imagenCliente = imagenCliente;
    }
}