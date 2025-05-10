package com.felicita.felicita.repository;

import com.felicita.felicita.model.Categoria;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repositorio para la entidad Categoria.
 * Proporciona métodos para acceder y manipular datos de categorías en la base de datos.
 */
@Repository
public interface CategoriaRepository extends JpaRepository<Categoria, Long> {
    
    /**
     * Busca categorías que estén activas
     * @return Lista de categorías activas
     */
    List<Categoria> findByActivoTrue();
    
    /**
     * Busca categorías activas ordenadas por el campo orden
     * @return Lista de categorías ordenadas
     */
    List<Categoria> findByActivoTrueOrderByOrdenAsc();
    
    /**
     * Busca una categoría por su nombre
     * @param nombre El nombre de la categoría a buscar
     * @return Un Optional que contiene la categoría si existe
     */
    Optional<Categoria> findByNombre(String nombre);
    
    /**
     * Busca categorías cuyo nombre contenga el texto proporcionado
     * @param nombre El texto a buscar en el nombre de la categoría
     * @return Lista de categorías que coinciden con el criterio
     */
    List<Categoria> findByNombreContainingAndActivoTrue(String nombre);
    
    /**
     * Verifica si existe una categoría con el nombre dado
     * @param nombre El nombre de la categoría a verificar
     * @return true si existe, false en caso contrario
     */
    boolean existsByNombre(String nombre);
}