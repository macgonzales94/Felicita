package com.felicita.felicita.model;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

/**
 * Clase que representa los servicios ofrecidos por el salón de belleza o barbería.
 * Contiene información como el nombre, descripción, precio y duración.
 */
@Entity
@Table(name = "servicios")
public class Servicio {
    /**
     * Identificador único del servicio
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre del servicio
     */
    @NotBlank
    @Column(name = "nombre")
    private String nombre;

    /**
     * Descripción detallada del servicio
     */
    @Column(name = "descripcion", columnDefinition = "TEXT")
    private String descripcion;

    /**
     * Precio del servicio
     */
    @NotNull
    @Positive
    @Column(name = "precio")
    private BigDecimal precio;

    /**
     * Duración estimada del servicio en minutos
     */
    @NotNull
    @Positive
    @Column(name = "duracion")
    private Integer duracion;

    /**
     * Ruta de la imagen representativa del servicio
     */
    @Column(name = "imagen")
    private String imagen;

    /**
     * Indica si el servicio está activo y disponible para reserva
     */
    @Column(name = "activo")
    private boolean activo = true;
    
    /**
     * Lista de reservas que incluyen este servicio
     */
    @OneToMany(mappedBy = "servicio")
    private List<ServicioReserva> serviciosReservas = new ArrayList<>();

    /**
     * Constructor por defecto
     */
    public Servicio() {
    }

    /**
     * Constructor con parámetros principales
     */
    public Servicio(String nombre, String descripcion, BigDecimal precio, Integer duracion) {
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.precio = precio;
        this.duracion = duracion;
    }

    // Getters y setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public BigDecimal getPrecio() {
        return precio;
    }

    public void setPrecio(BigDecimal precio) {
        this.precio = precio;
    }

    public Integer getDuracion() {
        return duracion;
    }

    public void setDuracion(Integer duracion) {
        this.duracion = duracion;
    }

    public String getImagen() {
        return imagen;
    }

    public void setImagen(String imagen) {
        this.imagen = imagen;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public List<ServicioReserva> getServiciosReservas() {
        return serviciosReservas;
    }

    public void setServiciosReservas(List<ServicioReserva> serviciosReservas) {
        this.serviciosReservas = serviciosReservas;
    }
}