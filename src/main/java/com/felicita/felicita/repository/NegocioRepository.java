package com.felicita.felicita.repository;

import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repositorio para la entidad Negocio.
 * Proporciona métodos para acceder y manipular datos de negocios en la base de datos.
 */
@Repository
public interface NegocioRepository extends JpaRepository<Negocio, Long> {
    
    /**
     * Busca un negocio por su usuario asociado
     * @param usuario El usuario cuyo negocio se quiere obtener
     * @return Un Optional que contiene el negocio si existe
     */
    Optional<Negocio> findByUsuario(Usuario usuario);
    
    /**
     * Busca negocios verificados
     * @return Lista de negocios verificados
     */
    List<Negocio> findByVerificadoTrue();
    
    /**
     * Busca negocios por estado
     * @param estado El estado a buscar
     * @return Lista de negocios con el estado especificado
     */
    List<Negocio> findByEstado(String estado);
    
    /**
     * Busca negocios por tipo
     * @param tipo El tipo a buscar
     * @return Lista de negocios del tipo especificado
     */
    List<Negocio> findByTipo(String tipo);
    
    /**
     * Busca negocios por nombre comercial que contenga el texto proporcionado
     * @param nombre El texto a buscar en el nombre comercial
     * @return Lista de negocios que coinciden con el criterio
     */
    List<Negocio> findByNombreComercialContainingAndEstado(String nombre, String estado);
    
    /**
     * Busca negocios cercanos a unas coordenadas específicas
     * @param latitud Latitud del punto central
     * @param longitud Longitud del punto central
     * @param distanciaKm Distancia máxima en kilómetros
     * @return Lista de negocios cercanos
     */
    @Query(value = "SELECT * FROM negocios n WHERE " +
            "(6371 * acos(cos(radians(?1)) * cos(radians(n.latitud)) * " +
            "cos(radians(n.longitud) - radians(?2)) + sin(radians(?1)) * " +
            "sin(radians(n.latitud)))) < ?3 AND n.estado = 'ACTIVO'", nativeQuery = true)
    List<Negocio> findNegociosCercanos(Double latitud, Double longitud, Double distanciaKm);
}