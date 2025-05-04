package com.felicita.felicita.model;

import javax.persistence.*;

/**
 * Clase que representa la relación entre servicios y reservas.
 * Permite que una reserva incluya múltiples servicios.
 */
@Entity
@Table(name = "servicios_reservas")
public class ServicioReserva {
    /**
     * Identificador único de la relación
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Reserva asociada
     */
    @ManyToOne
    @JoinColumn(name = "id_reserva")
    private Reserva reserva;

    /**
     * Servicio asociado
     */
    @ManyToOne
    @JoinColumn(name = "id_servicio")
    private Servicio servicio;

    /**
     * Constructor por defecto
     */
    public ServicioReserva() {
    }

    /**
     * Constructor con parámetros principales
     */
    public ServicioReserva(Reserva reserva, Servicio servicio) {
        this.reserva = reserva;
        this.servicio = servicio;
    }

    // Getters y setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Reserva getReserva() {
        return reserva;
    }

    public void setReserva(Reserva reserva) {
        this.reserva = reserva;
    }

    public Servicio getServicio() {
        return servicio;
    }

    public void setServicio(Servicio servicio) {
        this.servicio = servicio;
    }
}