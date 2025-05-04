package com.felicita.felicita.controller;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.service.UsuarioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Controlador REST para operaciones relacionadas con usuarios.
 */
@RestController
@RequestMapping("/api/usuarios")
public class UsuarioRestController {

    @Autowired
    private UsuarioService usuarioService;

    /**
     * Obtiene todos los usuarios (solo para admin)
     * @return Lista de usuarios
     */
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<Usuario>> obtenerTodos() {
        List<Usuario> usuarios = usuarioService.obtenerTodos();
        return new ResponseEntity<>(usuarios, HttpStatus.OK);
    }

    /**
     * Obtiene un usuario por su ID
     * @param id ID del usuario
     * @return Usuario si existe
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or @seguridadService.esUsuarioActual(#id)")
    public ResponseEntity<Usuario> obtenerPorId(@PathVariable Long id) {
        return usuarioService.obtenerPorId(id)
                .map(usuario -> new ResponseEntity<>(usuario, HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    /**
     * Actualiza un usuario
     * @param id ID del usuario
     * @param usuario Datos actualizados
     * @return Mensaje de respuesta
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or @seguridadService.esUsuarioActual(#id)")
    public ResponseEntity<MensajeResponse> actualizar(@PathVariable Long id, @Valid @RequestBody Usuario usuario) {
        MensajeResponse respuesta = usuarioService.actualizarUsuario(id, usuario);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }

    /**
     * Cambia el rol de un usuario (solo admin)
     * @param id ID del usuario
     * @param rol Nuevo rol
     * @return Mensaje de respuesta
     */
    @PatchMapping("/{id}/rol")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> cambiarRol(@PathVariable Long id, @RequestParam String rol) {
        MensajeResponse respuesta = usuarioService.cambiarRol(id, rol);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }

    /**
     * Elimina un usuario (solo admin)
     * @param id ID del usuario
     * @return Mensaje de respuesta
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> eliminar(@PathVariable Long id) {
        MensajeResponse respuesta = usuarioService.eliminarUsuario(id);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.NOT_FOUND);
        }
    }
}