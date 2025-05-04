package com.felicita.felicita.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Clase que representa a los usuarios del sistema FELICITA.
 * Almacena la información de clientes y administradores.
 */
@Entity
@Table(name = "usuarios", 
       uniqueConstraints = {
           @UniqueConstraint(columnNames = "nombreUsuario"),
           @UniqueConstraint(columnNames = "correo")
       })
public class Usuario {
    /**
     * Identificador único del usuario
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre de usuario para iniciar sesión
     */
    @NotBlank
    @Size(max = 20)
    @Column(name = "nombreUsuario")
    private String nombreUsuario;

    /**
     * Correo electrónico del usuario
     */
    @NotBlank
    @Size(max = 50)
    @Email
    @Column(name = "correo")
    private String correo;

    /**
     * Contraseña encriptada del usuario
     */
    @NotBlank
    @Size(max = 120)
    @Column(name = "contraseña")
    private String contraseña;
    
    /**
     * Nombre completo del usuario
     */
    @NotBlank
    @Size(max = 100)
    @Column(name = "nombreCompleto")
    private String nombreCompleto;
    
    /**
     * Número de teléfono del usuario
     */
    @Size(max = 20)
    @Column(name = "telefono")
    private String telefono;
    
    /**
     * Rol del usuario (ADMIN o CLIENTE)
     */
    @NotBlank
    @Column(name = "rol")
    private String rol;
    
    /**
     * Fecha y hora de creación de la cuenta
     */
    @Column(name = "fechaCreacion")
    private LocalDateTime fechaCreacion;
    
    /**
     * Lista de reservas realizadas por el usuario
     */
    @OneToMany(mappedBy = "usuario", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Reserva> reservas = new ArrayList<>();

    /**
     * Constructor por defecto
     */
    public Usuario() {
        this.fechaCreacion = LocalDateTime.now();
    }

    /**
     * Constructor con parámetros principales
     */
    public Usuario(String nombreUsuario, String correo, String contraseña, String nombreCompleto, String telefono) {
        this.nombreUsuario = nombreUsuario;
        this.correo = correo;
        this.contraseña = contraseña;
        this.nombreCompleto = nombreCompleto;
        this.telefono = telefono;
        this.fechaCreacion = LocalDateTime.now();
    }

    // Getters y setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

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

    public String getRol() {
        return rol;
    }

    public void setRol(String rol) {
        this.rol = rol;
    }

    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }

    public void setFechaCreacion(LocalDateTime fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }

    public List<Reserva> getReservas() {
        return reservas;
    }

    public void setReservas(List<Reserva> reservas) {
        this.reservas = reservas;
    }
}