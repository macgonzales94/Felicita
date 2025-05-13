package com.felicita.felicita.repository;

import com.felicita.felicita.model.Usuario;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repositorio para la entidad Usuario.
 * Proporciona métodos para acceder y manipular datos de usuarios en la base de datos.
 */
@Repository
public interface UsuarioRepository extends JpaRepository<Usuario, Long> {
    
    /**
     * Busca un usuario por su nombre de usuario
     * @param nombreUsuario El nombre de usuario a buscar
     * @return Un Optional que contiene el usuario si existe
     */
    Optional<Usuario> findByNombreUsuario(String nombreUsuario);
    
    /**
     * Método alternativo para buscar un usuario por su nombre de usuario 
     * (para compatibilidad con Spring Security)
     * @param username El nombre de usuario a buscar
     * @return Un Optional que contiene el usuario si existe
     */
    default Optional<Usuario> findByUsername(String username) {
        return findByNombreUsuario(username);
    }
    
    /**
     * Busca un usuario por su correo electrónico
     * @param correo El correo electrónico a buscar
     * @return Un Optional que contiene el usuario si existe
     */
    Optional<Usuario> findByCorreo(String correo);
    
    /**
     * Verifica si existe un usuario con el nombre de usuario dado
     * @param nombreUsuario El nombre de usuario a verificar
     * @return true si existe, false en caso contrario
     */
    Boolean existsByNombreUsuario(String nombreUsuario);
    
    /**
     * Verifica si existe un usuario con el correo electrónico dado
     * @param correo El correo electrónico a verificar
     * @return true si existe, false en caso contrario
     */
    Boolean existsByCorreo(String correo);
}