package com.felicita.felicita.repository;

import com.felicita.felicita.model.Disponibilidad;
import com.felicita.felicita.model.Empleado;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Repositorio para la entidad Disponibilidad.
 * Proporciona métodos para acceder y manipular datos de disponibilidad de empleados.
 */
@Repository
public interface DisponibilidadRepository extends JpaRepository<Disponibilidad, Long> {
    
    /**
     * Busca disponibilidades por empleado
     * @param empleado El empleado cuyas disponibilidades se quieren obtener
     * @return Lista de disponibilidades del empleado
     */
    List<Disponibilidad> findByEmpleado(Empleado empleado);
    
    /**
     * Busca disponibilidades por día
     * @param dia El día para el cual se quieren obtener las disponibilidades
     * @return Lista de disponibilidades para el día especificado
     */
    List<Disponibilidad> findByDia(LocalDate dia);
    
    /**
     * Busca disponibilidades por empleado y día
     * @param empleado El empleado cuyas disponibilidades se quieren obtener
     * @param dia El día para el cual se quieren obtener las disponibilidades
     * @return Lista de disponibilidades del empleado para el día especificado
     */
    List<Disponibilidad> findByEmpleadoAndDia(Empleado empleado, LocalDate dia);
    
    /**
     * Busca disponibilidades de empleados activos para un día específico
     * @param dia El día para el cual se quieren obtener las disponibilidades
     * @param disponible Valor booleano que indica si están disponibles o no
     * @return Lista de disponibilidades para el día y estado de disponibilidad especificados
     */
    List<Disponibilidad> findByDiaAndDisponible(LocalDate dia, boolean disponible);
    
    /**
     * Busca disponibilidades en un rango de fechas
     * @param inicio Fecha de inicio del rango
     * @param fin Fecha de fin del rango
     * @return Lista de disponibilidades en el rango de fechas especificado
     */
    List<Disponibilidad> findByDiaBetween(LocalDate inicio, LocalDate fin);
}