// src/main/java/com/felicita/felicita/model/Reserva.java
package com.felicita.felicita.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;

/**
 * Clase que representa las reservas o citas en el sistema.
 * Relaciona usuarios, empleados y servicios en una fecha y hora específica.
 */
@Entity
@Table(name = "reservas")
public class Reserva {
    /**
     * Identificador único de la reserva
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Usuario que realiza la reserva
     */
    @ManyToOne
    @JoinColumn(name = "id_usuario", nullable = false)
    private Usuario usuario;

    /**
     * Empleado asignado para atender la reserva
     */
    @ManyToOne
    @JoinColumn(name = "id_empleado")
    private Empleado empleado;

    /**
     * Fecha y hora de inicio de la reserva
     */
    @NotNull
    @Column(name = "hora_inicio")
    private LocalDateTime horaInicio;

    /**
     * Fecha y hora de finalización de la reserva
     */
    @NotNull
    @Column(name = "hora_fin")
    private LocalDateTime horaFin;

    /**
     * Estado actual de la reserva
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "estado")
    private EstadoReserva estado;

    /**
     * Notas adicionales sobre la reserva
     */
    @Column(name = "notas")
    private String notas;

    /**
     * Fecha y hora de creación de la reserva
     */
    @Column(name = "fecha_creacion")
    private LocalDateTime fechaCreacion;
    
    /**
     * Lista de servicios incluidos en la reserva
     */
    @OneToMany(mappedBy = "reserva", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ServicioReserva> serviciosReservas = new ArrayList<>();

    /**
     * Enumeración para los posibles estados de una reserva
     */
    public enum EstadoReserva {
        PENDIENTE, CONFIRMADA, CANCELADA, COMPLETADA
    }

    /**
     * Constructor por defecto
     */
    public Reserva() {
        this.fechaCreacion = LocalDateTime.now();
        this.estado = EstadoReserva.PENDIENTE;
    }

    // Getters y setters (manteniendo los mismos)
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public void setUsuario(Usuario usuario) {
        this.usuario = usuario;
    }

    public Empleado getEmpleado() {
        return empleado;
    }

    public void setEmpleado(Empleado empleado) {
        this.empleado = empleado;
    }

    public LocalDateTime getHoraInicio() {
        return horaInicio;
    }

    public void setHoraInicio(LocalDateTime horaInicio) {
        this.horaInicio = horaInicio;
    }

    public LocalDateTime getHoraFin() {
        return horaFin;
    }

    public void setHoraFin(LocalDateTime horaFin) {
        this.horaFin = horaFin;
    }

    public EstadoReserva getEstado() {
        return estado;
    }

    public void setEstado(EstadoReserva estado) {
        this.estado = estado;
    }

    public String getNotas() {
        return notas;
    }

    public void setNotas(String notas) {
        this.notas = notas;
    }

    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }

    public void setFechaCreacion(LocalDateTime fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }

    public List<ServicioReserva> getServiciosReservas() {
        return serviciosReservas;
    }

    public void setServiciosReservas(List<ServicioReserva> serviciosReservas) {
        this.serviciosReservas = serviciosReservas;
    }
    
    /**
     * Método para agregar un servicio a la reserva
     * @param servicio El servicio a agregar
     */
    public void agregarServicio(Servicio servicio) {
        ServicioReserva servicioReserva = new ServicioReserva(this, servicio);
        this.serviciosReservas.add(servicioReserva);
    }
}