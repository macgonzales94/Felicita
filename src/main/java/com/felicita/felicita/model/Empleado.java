package com.felicita.felicita.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.ArrayList;
import java.util.List;

/**
 * Clase que representa los empleados del salón de belleza o barbería.
 * Permite organizar los servicios en grupos para su mejor visualización y filtrado.
 */
@Entity
@Table(name = "empleados")
public class Empleado {
    /**
     * Identificador único del empleado
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre completo del empleado
     */
    @NotBlank
    @Column(name = "nombre")
    private String nombre;

    /**
     * Cargo o posición del empleado (ej: Estilista, Barbero, etc.)
     */
    @Column(name = "cargo")
    private String cargo;

    /**
     * Ruta de la foto del empleado
     */
    @Column(name = "foto")
    private String foto;

    /**
     * Indica si el empleado está activo
     */
    @Column(name = "activo")
    private boolean activo = true;
    
    /**
     * Descripción o biografía del empleado
     */
    @Column(name = "biografia", columnDefinition = "TEXT")
    private String biografia;
    
    /**
     * Calificación promedio del empleado (1-5 estrellas)
     */
    @Column(name = "calificacion")
    private Float calificacion;
    
    /**
     * Correo electrónico del empleado
     */
    @Column(name = "correo")
    private String correo;
    
    /**
     * Teléfono del empleado
     */
    @Column(name = "telefono")
    @Size(max = 20)
    private String telefono;
    
    /**
     * Negocio al que pertenece el empleado
     */
    @ManyToOne
    @JoinColumn(name = "id_negocio")
    private Negocio negocio;

    /**
     * Lista de reservas asignadas al empleado
     */
    @OneToMany(mappedBy = "empleado")
    private List<Reserva> reservas = new ArrayList<>();
    
    /**
     * Lista de disponibilidades del empleado
     */
    @OneToMany(mappedBy = "empleado", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Disponibilidad> disponibilidades = new ArrayList<>();

    /**
     * Constructor por defecto
     */
    public Empleado() {
    }

    /**
     * Constructor con parámetros principales
     */
    public Empleado(String nombre, String cargo) {
        this.nombre = nombre;
        this.cargo = cargo;
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

    public String getCargo() {
        return cargo;
    }

    public void setCargo(String cargo) {
        this.cargo = cargo;
    }

    public String getFoto() {
        return foto;
    }

    public void setFoto(String foto) {
        this.foto = foto;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public List<Reserva> getReservas() {
        return reservas;
    }

    public void setReservas(List<Reserva> reservas) {
        this.reservas = reservas;
    }
    
    public List<Disponibilidad> getDisponibilidades() {
        return disponibilidades;
    }

    public void setDisponibilidades(List<Disponibilidad> disponibilidades) {
        this.disponibilidades = disponibilidades;
    }
    
    public String getBiografia() {
        return biografia;
    }

    public void setBiografia(String biografia) {
        this.biografia = biografia;
    }

    public Float getCalificacion() {
        return calificacion;
    }

    public void setCalificacion(Float calificacion) {
        this.calificacion = calificacion;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public Negocio getNegocio() {
        return negocio;
    }

    public void setNegocio(Negocio negocio) {
        this.negocio = negocio;
    }
}