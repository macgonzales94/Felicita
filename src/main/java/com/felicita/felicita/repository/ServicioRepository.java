package com.felicita.felicita.repository;

import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.model.Servicio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repositorio para la entidad Servicio.
 * Proporciona métodos para acceder y manipular datos de servicios en la base de datos.
 */
@Repository
public interface ServicioRepository extends JpaRepository<Servicio, Long> {
    
    /**
     * Busca servicios por nombre que contengan el texto proporcionado
     * @param nombre El texto a buscar en el nombre del servicio
     * @return Lista de servicios que coinciden con el criterio
     */
    List<Servicio> findByNombreContaining(String nombre);
    
    /**
     * Busca servicios que estén activos
     * @return Lista de servicios activos
     */
    List<Servicio> findByActivoTrue();
    
    /**
     * Busca servicios por rango de precio (desde un mínimo hasta un máximo)
     * @param precioMin Precio mínimo
     * @param precioMax Precio máximo
     * @return Lista de servicios dentro del rango de precio
     */
    List<Servicio> findByPrecioBetween(Double precioMin, Double precioMax);
    
    /**
     * Busca servicios con duración menor o igual al valor proporcionado
     * @param duracionMaxima Duración máxima en minutos
     * @return Lista de servicios con duración menor o igual
     */
    List<Servicio> findByDuracionLessThanEqual(Integer duracionMaxima);
    
    /**
     * Busca servicios por negocio
     * @param negocio El negocio cuyos servicios se quieren obtener
     * @return Lista de servicios del negocio especificado
     */
    List<Servicio> findByNegocio(Negocio negocio);
    
    /**
     * Busca servicios activos por negocio
     * @param negocio El negocio cuyos servicios activos se quieren obtener
     * @return Lista de servicios activos del negocio especificado
     */
    List<Servicio> findByNegocioAndActivoTrue(Negocio negocio);
}