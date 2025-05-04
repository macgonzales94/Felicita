package com.felicita.felicita.model;

import java.util.ArrayList;
import java.util.List;

import javax.persistence.*;
import javax.validation.constraints.NotBlank;

/**
 * Clase que representa a los empleados del salón de belleza o barbería.
 * Almacena información como nombre, cargo y disponibilidad.
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
     * Indica si el empleado está activo en el sistema
     */
    @Column(name = "activo")
    private boolean activo = true;
    
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
}