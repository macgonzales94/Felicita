package com.felicita.felicita.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.ArrayList;
import java.util.List;

/**
 * Clase que representa las categorías de servicios.
 * Permite organizar los servicios en grupos para su mejor visualización y filtrado.
 */
@Entity
@Table(name = "categorias")
public class Categoria {
    /**
     * Identificador único de la categoría
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre de la categoría
     */
    @NotBlank
    @Size(max = 50)
    @Column(name = "nombre")
    private String nombre;

    /**
     * Descripción de la categoría
     */
    @Size(max = 255)
    @Column(name = "descripcion")
    private String descripcion;

    /**
     * Icono de Font Awesome para representar la categoría
     * (ej: "fa-scissors", "fa-nail-polish", etc.)
     */
    @Column(name = "icono")
    private String icono;

    /**
     * Indica si la categoría está activa
     */
    @Column(name = "activo")
    private boolean activo = true;
    
    /**
     * Orden de aparición de la categoría
     */
    @Column(name = "orden")
    private Integer orden;
    
    /**
     * Lista de servicios relacionados con esta categoría
     */
    @OneToMany(mappedBy = "categoria")
    private List<Servicio> servicios = new ArrayList<>();

    /**
     * Constructor por defecto
     */
    public Categoria() {
    }

    /**
     * Constructor con parámetros principales
     */
    public Categoria(String nombre, String descripcion) {
        this.nombre = nombre;
        this.descripcion = descripcion;
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

    public String getIcono() {
        return icono;
    }

    public void setIcono(String icono) {
        this.icono = icono;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public Integer getOrden() {
        return orden;
    }

    public void setOrden(Integer orden) {
        this.orden = orden;
    }

    public List<Servicio> getServicios() {
        return servicios;
    }

    public void setServicios(List<Servicio> servicios) {
        this.servicios = servicios;
    }
}