package com.felicita.felicita.repository;

import com.felicita.felicita.model.Testimonio;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.model.Servicio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repositorio para la entidad Testimonio.
 * Proporciona métodos para acceder y manipular datos de testimonios en la base de datos.
 */
@Repository
public interface TestimonioRepository extends JpaRepository<Testimonio, Long> {
    
    /**
     * Busca testimonios que estén activos
     * @return Lista de testimonios activos
     */
    List<Testimonio> findByActivoTrue();
    
    /**
     * Busca testimonios por usuario
     * @param usuario El usuario cuyas testimonios se quieren obtener
     * @return Lista de testimonios del usuario
     */
    List<Testimonio> findByUsuario(Usuario usuario);
    
    /**
     * Busca testimonios por servicio
     * @param servicio El servicio cuyos testimonios se quieren obtener
     * @return Lista de testimonios del servicio
     */
    List<Testimonio> findByServicio(Servicio servicio);
    
    /**
     * Busca testimonios activos con mejor valoración
     * @param limit Límite de testimonios a retornar
     * @return Lista de testimonios con mejor valoración
     */
    @Query("SELECT t FROM Testimonio t WHERE t.activo = true ORDER BY t.valoracion DESC, t.fecha DESC")
    List<Testimonio> findTopTestimoniosByValoracion(int limit);
    
    /**
     * Busca testimonios activos más recientes
     * @param limit Límite de testimonios a retornar
     * @return Lista de testimonios más recientes
     */
    @Query("SELECT t FROM Testimonio t WHERE t.activo = true ORDER BY t.fecha DESC")
    List<Testimonio> findTopTestimoniosByFecha(int limit);
    
    /**
     * Calcula la valoración promedio de un servicio
     * @param servicioId ID del servicio
     * @return Valoración promedio del servicio
     */
    @Query("SELECT AVG(t.valoracion) FROM Testimonio t WHERE t.servicio.id = :servicioId AND t.activo = true")
    Double calcularValoracionPromedioPorServicio(Long servicioId);
    
    /**
     * Cuenta la cantidad de testimonios por valoración para un servicio
     * @param servicioId ID del servicio
     * @param valoracion Valoración (1-5)
     * @return Cantidad de testimonios
     */
    Long countByServicioIdAndValoracionAndActivoTrue(Long servicioId, Integer valoracion);
}