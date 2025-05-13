package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Servicio que gestiona las operaciones relacionadas con los usuarios.
 */
@Service
public class UsuarioService {

    @Autowired
    private UsuarioRepository usuarioRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    /**
     * Obtiene todos los usuarios del sistema
     * @return Lista de usuarios
     */
    public List<Usuario> obtenerTodos() {
        return usuarioRepository.findAll();
    }
    
    /**
     * Busca un usuario por su ID
     * @param id ID del usuario
     * @return Usuario si existe, vacío si no
     */
    public Optional<Usuario> obtenerPorId(Long id) {
        return usuarioRepository.findById(id);
    }
    
    /**
     * Busca un usuario por su nombre de usuario
     * @param nombreUsuario Nombre de usuario
     * @return Usuario si existe, vacío si no
     */
    public Optional<Usuario> obtenerPorNombreUsuario(String nombreUsuario) {
        return usuarioRepository.findByNombreUsuario(nombreUsuario);
    }
    
    /**
     * Actualiza la información de un usuario
     * @param id ID del usuario a actualizar
     * @param usuarioDetalles Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarUsuario(Long id, Usuario usuarioDetalles) {
        return usuarioRepository.findById(id)
            .map(usuario -> {
                // No actualizar nombre de usuario ni correo para evitar duplicados
                usuario.setNombreCompleto(usuarioDetalles.getNombreCompleto());
                usuario.setTelefono(usuarioDetalles.getTelefono());
                
                // Solo actualizar contraseña si se proporciona una nueva
                if (usuarioDetalles.getContraseña() != null && !usuarioDetalles.getContraseña().isEmpty()) {
                    usuario.setContraseña(passwordEncoder.encode(usuarioDetalles.getContraseña()));
                }
                
                usuarioRepository.save(usuario);
                return new MensajeResponse("Usuario actualizado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el usuario con ID: " + id, false));
    }
    
    /**
     * Cambia el rol de un usuario
     * @param id ID del usuario
     * @param nuevoRol Nuevo rol a asignar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarRol(Long id, String nuevoRol) {
        return usuarioRepository.findById(id)
            .map(usuario -> {
                usuario.setRol(nuevoRol);
                usuarioRepository.save(usuario);
                return new MensajeResponse("Rol actualizado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el usuario con ID: " + id, false));
    }
    
    /**
     * Elimina un usuario del sistema
     * @param id ID del usuario a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarUsuario(Long id) {
        return usuarioRepository.findById(id)
            .map(usuario -> {
                usuarioRepository.delete(usuario);
                return new MensajeResponse("Usuario eliminado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el usuario con ID: " + id, false));
    }

    /**
 * Busca un usuario por su nombre de usuario
 * @param username El nombre de usuario a buscar
 * @return Usuario si existe, vacío si no
 */
public Optional<Usuario> findByUsername(String username) {
    return usuarioRepository.findByNombreUsuario(username);
}

}