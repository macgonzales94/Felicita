package com.felicita.felicita.repository;

import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Negocio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repositorio para la entidad Empleado.
 * Proporciona métodos para acceder y manipular datos de empleados en la base de datos.
 */
@Repository
public interface EmpleadoRepository extends JpaRepository<Empleado, Long> {
    
    /**
     * Busca empleados por nombre que contengan el texto proporcionado
     * @param nombre El texto a buscar en el nombre del empleado
     * @return Lista de empleados que coinciden con el criterio
     */
    List<Empleado> findByNombreContaining(String nombre);
    
    /**
     * Busca empleados por cargo
     * @param cargo El cargo a buscar
     * @return Lista de empleados con el cargo especificado
     */
    List<Empleado> findByCargo(String cargo);
    
    /**
     * Busca empleados que estén activos
     * @return Lista de empleados activos
     */
    List<Empleado> findByActivoTrue();
    
    /**
     * Busca empleados por negocio
     * @param negocio El negocio cuyos empleados se quieren obtener
     * @return Lista de empleados del negocio especificado
     */
    List<Empleado> findByNegocio(Negocio negocio);
    
    /**
     * Busca empleados activos por negocio
     * @param negocio El negocio cuyos empleados activos se quieren obtener
     * @return Lista de empleados activos del negocio especificado
     */
    List<Empleado> findByNegocioAndActivoTrue(Negocio negocio);
}