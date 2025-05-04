package com.felicita.felicita.repository;

import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.ServicioReserva;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repositorio para la entidad ServicioReserva.
 * Proporciona métodos para acceder y manipular datos de la relación entre servicios y reservas.
 */
@Repository
public interface ServicioReservaRepository extends JpaRepository<ServicioReserva, Long> {
    
    /**
     * Busca relaciones por reserva
     * @param reserva La reserva cuyos servicios se quieren obtener
     * @return Lista de relaciones ServicioReserva asociadas a la reserva
     */
    List<ServicioReserva> findByReserva(Reserva reserva);
    
    /**
     * Busca relaciones por servicio
     * @param servicio El servicio cuyas reservas se quieren obtener
     * @return Lista de relaciones ServicioReserva asociadas al servicio
     */
    List<ServicioReserva> findByServicio(Servicio servicio);
}