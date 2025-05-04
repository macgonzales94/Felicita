// src/main/java/com/felicita/felicita/model/Disponibilidad.java
package com.felicita.felicita.model;

import java.time.LocalDate;
import java.time.LocalTime;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;

/**
 * Clase que representa la disponibilidad horaria de los empleados.
 * Permite definir los días y horarios en que cada empleado está disponible.
 */
@Entity
@Table(name = "disponibilidades")
public class Disponibilidad {
    /**
     * Identificador único de la disponibilidad
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Empleado asociado a esta disponibilidad
     */
    @ManyToOne
    @JoinColumn(name = "id_empleado", nullable = false)
    private Empleado empleado;

    /**
     * Fecha específica de disponibilidad
     */
    @NotNull
    @Column(name = "dia")
    private LocalDate dia;

    /**
     * Hora de inicio de la disponibilidad
     */
    @NotNull
    @Column(name = "hora_inicio")
    private LocalTime horaInicio;

    /**
     * Hora de fin de la disponibilidad
     */
    @NotNull
    @Column(name = "hora_fin")
    private LocalTime horaFin;

    /**
     * Indica si el horario está disponible o no (ej: vacaciones, ausencias)
     */
    @Column(name = "disponible")
    private boolean disponible = true;

    /**
     * Constructor por defecto
     */
    public Disponibilidad() {
    }

    /**
     * Constructor con parámetros principales
     */
    public Disponibilidad(Empleado empleado, LocalDate dia, LocalTime horaInicio, LocalTime horaFin) {
        this.empleado = empleado;
        this.dia = dia;
        this.horaInicio = horaInicio;
        this.horaFin = horaFin;
    }

    // Getters y setters (manteniendo los mismos)
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Empleado getEmpleado() {
        return empleado;
    }

    public void setEmpleado(Empleado empleado) {
        this.empleado = empleado;
    }

    public LocalDate getDia() {
        return dia;
    }

    public void setDia(LocalDate dia) {
        this.dia = dia;
    }

    public LocalTime getHoraInicio() {
        return horaInicio;
    }

    public void setHoraInicio(LocalTime horaInicio) {
        this.horaInicio = horaInicio;
    }

    public LocalTime getHoraFin() {
        return horaFin;
    }

    public void setHoraFin(LocalTime horaFin) {
        this.horaFin = horaFin;
    }

    public boolean isDisponible() {
        return disponible;
    }

    public void setDisponible(boolean disponible) {
        this.disponible = disponible;
    }
}