package com.felicita.felicita.repository;

import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Reserva.EstadoReserva;
import com.felicita.felicita.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repositorio para la entidad Reserva.
 * Proporciona métodos para acceder y manipular datos de reservas en la base de datos.
 */
@Repository
public interface ReservaRepository extends JpaRepository<Reserva, Long> {
    
    /**
     * Busca reservas por usuario
     * @param usuario El usuario cuyas reservas se quieren obtener
     * @return Lista de reservas del usuario
     */
    List<Reserva> findByUsuario(Usuario usuario);
    
    /**
     * Busca reservas por empleado
     * @param empleado El empleado cuyas reservas se quieren obtener
     * @return Lista de reservas del empleado
     */
    List<Reserva> findByEmpleado(Empleado empleado);
    
    /**
     * Busca reservas por estado
     * @param estado El estado de las reservas a buscar
     * @return Lista de reservas con el estado especificado
     */
    List<Reserva> findByEstado(EstadoReserva estado);
    
    /**
     * Busca reservas cuya hora de inicio esté entre dos fechas
     * @param inicio Fecha y hora de inicio del período
     * @param fin Fecha y hora de fin del período
     * @return Lista de reservas en el período especificado
     */
    List<Reserva> findByHoraInicioBetween(LocalDateTime inicio, LocalDateTime fin);
    
    /**
     * Busca reservas por usuario y estado
     * @param usuario El usuario cuyas reservas se quieren obtener
     * @param estado El estado de las reservas a buscar
     * @return Lista de reservas del usuario con el estado especificado
     */
    List<Reserva> findByUsuarioAndEstado(Usuario usuario, EstadoReserva estado);
    
    /**
     * Busca reservas cuya fecha de creación sea posterior a la fecha proporcionada
     * @param fecha La fecha a partir de la cual buscar reservas
     * @return Lista de reservas creadas después de la fecha
     */
    List<Reserva> findByFechaCreacionAfter(LocalDateTime fecha);
    
    /**
     * Busca reservas que pertenecen a alguno de los empleados de la lista
     * @param empleados Lista de empleados cuyas reservas se quieren obtener
     * @return Lista de reservas asociadas a los empleados
     */
    List<Reserva> findByEmpleadoIn(List<Empleado> empleados);
    
    /**
     * Busca reservas recientes ordenadas por fecha de creación
     * @return Lista de reservas ordenadas por fecha de creación descendente
     */
    List<Reserva> findAllByOrderByFechaCreacionDesc();
    
    /**
     * Busca reservas cuya hora de inicio sea posterior a la fecha proporcionada
     * @param fecha La fecha a partir de la cual buscar reservas
     * @return Lista de reservas con hora de inicio posterior a la fecha
     */
    List<Reserva> findByHoraInicioAfter(LocalDateTime fecha);
    
    /**
     * Busca reservas por empleado y estado
     * @param empleado El empleado cuyas reservas se quieren obtener
     * @param estado El estado de las reservas a buscar
     * @return Lista de reservas del empleado con el estado especificado
     */
    List<Reserva> findByEmpleadoAndEstado(Empleado empleado, EstadoReserva estado);
}