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
     * Categoría a la que pertenece el servicio
     */
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "id_categoria")
    private Categoria categoria;
    
    /**
     * Indica si el servicio es destacado para mostrarlo en página principal
     */
    @Column(name = "destacado")
    private boolean destacado = false;
    
    /**
     * Calificación promedio del servicio (1-5 estrellas)
     */
    @Column(name = "calificacion")
    private Float calificacion;
    
    /**
     * Número de calificaciones recibidas
     */
    @Column(name = "num_calificaciones")
    private Integer numCalificaciones = 0;
    
    /**
     * Lista de reservas que incluyen este servicio
     */
    @OneToMany(mappedBy = "servicio")
    private List<ServicioReserva> serviciosReservas = new ArrayList<>();
    
    /**
     * Lista de testimonios del servicio
     */
    @OneToMany(mappedBy = "servicio")
    private List<Testimonio> testimonios = new ArrayList<>();
    
    /**
     * Negocio que ofrece este servicio
     */
    @ManyToOne
    @JoinColumn(name = "id_negocio")
    private Negocio negocio;

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

    // Getters y setters existentes...
    
    public Negocio getNegocio() {
        return negocio;
    }

    public void setNegocio(Negocio negocio) {
        this.negocio = negocio;
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
    
    public Categoria getCategoria() {
        return categoria;
    }

    public void setCategoria(Categoria categoria) {
        this.categoria = categoria;
    }

    public boolean isDestacado() {
        return destacado;
    }

    public void setDestacado(boolean destacado) {
        this.destacado = destacado;
    }

    public Float getCalificacion() {
        return calificacion;
    }

    public void setCalificacion(Float calificacion) {
        this.calificacion = calificacion;
    }

    public Integer getNumCalificaciones() {
        return numCalificaciones;
    }

    public void setNumCalificaciones(Integer numCalificaciones) {
        this.numCalificaciones = numCalificaciones;
    }
    
    public List<Testimonio> getTestimonios() {
        return testimonios;
    }

    public void setTestimonios(List<Testimonio> testimonios) {
        this.testimonios = testimonios;
    }
    
    /**
     * Añade una nueva calificación al servicio y actualiza la calificación promedio
     * @param nuevaCalificacion Valor de la nueva calificación (1-5)
     */
    public void agregarCalificacion(int nuevaCalificacion) {
        if (nuevaCalificacion < 1 || nuevaCalificacion > 5) {
            throw new IllegalArgumentException("La calificación debe estar entre 1 y 5");
        }
        
        if (this.calificacion == null) {
            this.calificacion = (float) nuevaCalificacion;
            this.numCalificaciones = 1;
        } else {
            float totalActual = this.calificacion * this.numCalificaciones;
            this.numCalificaciones++;
            this.calificacion = (totalActual + nuevaCalificacion) / this.numCalificaciones;
        }
    }
}