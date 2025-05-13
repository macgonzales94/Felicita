package com.felicita.felicita.controller;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.service.NegocioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.List;

/**
 * Controlador REST para operaciones relacionadas con negocios.
 */
@RestController
@RequestMapping("/api/negocios")
public class NegocioController {

    @Autowired
    private NegocioService negocioService;

    /**
     * Obtiene todos los negocios (solo para admin)
     * @return Lista de negocios
     */
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<Negocio>> obtenerTodos() {
        List<Negocio> negocios = negocioService.obtenerTodos();
        return new ResponseEntity<>(negocios, HttpStatus.OK);
    }
    
    /**
     * Obtiene negocios activos (públicamente accesible)
     * @return Lista de negocios activos
     */
    @GetMapping("/activos")
    public ResponseEntity<List<Negocio>> obtenerActivos() {
        List<Negocio> negocios = negocioService.obtenerNegociosActivos();
        return new ResponseEntity<>(negocios, HttpStatus.OK);
    }

    /**
     * Obtiene un negocio por su ID
     * @param id ID del negocio
     * @return Negocio si existe
     */
    @GetMapping("/{id}")
    public ResponseEntity<Negocio> obtenerPorId(@PathVariable Long id) {
        return negocioService.obtenerPorId(id)
                .map(negocio -> new ResponseEntity<>(negocio, HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    
    /**
     * Busca un negocio por usuario
     * @param usuarioId ID del usuario
     * @return Negocio si existe
     */
    @GetMapping("/usuario/{usuarioId}")
    @PreAuthorize("hasRole('ADMIN') or @seguridadService.esUsuarioActual(#usuarioId)")
    public ResponseEntity<Negocio> obtenerPorUsuario(@PathVariable Long usuarioId) {
        return negocioService.obtenerPorUsuario(usuarioId)
                .map(negocio -> new ResponseEntity<>(negocio, HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }
    
    /**
     * Busca negocios cercanos a una ubicación
     * @param latitud Latitud del punto central
     * @param longitud Longitud del punto central
     * @param distancia Distancia en kilómetros
     * @return Lista de negocios cercanos
     */
    @GetMapping("/cercanos")
    public ResponseEntity<List<Negocio>> buscarCercanos(
            @RequestParam Double latitud,
            @RequestParam Double longitud,
            @RequestParam(defaultValue = "5") Double distancia) {
        List<Negocio> negocios = negocioService.buscarNegociosCercanos(latitud, longitud, distancia);
        return new ResponseEntity<>(negocios, HttpStatus.OK);
    }

    /**
     * Crea un nuevo negocio (solo admin)
     * @param usuarioId ID del usuario propietario
     * @param negocio Datos del negocio
     * @return Mensaje de respuesta
     */
    @PostMapping("/usuario/{usuarioId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> crear(@PathVariable Long usuarioId, @Valid @RequestBody Negocio negocio) {
        MensajeResponse respuesta = negocioService.crearNegocio(usuarioId, negocio);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.CREATED);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }

    /**
     * Actualiza los datos de un negocio
     * @param id ID del negocio
     * @param negocio Datos actualizados
     * @return Mensaje de respuesta
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or @negocioAutorizacionService.esPropietarioNegocio(#id)")
    public ResponseEntity<MensajeResponse> actualizar(@PathVariable Long id, @Valid @RequestBody Negocio negocio) {
        MensajeResponse respuesta = negocioService.actualizarNegocio(id, negocio);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }
    
    /**
     * Cambia el estado de un negocio (solo admin)
     * @param id ID del negocio
     * @param estado Nuevo estado
     * @return Mensaje de respuesta
     */
    @PatchMapping("/{id}/estado")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> cambiarEstado(@PathVariable Long id, @RequestParam String estado) {
        MensajeResponse respuesta = negocioService.cambiarEstado(id, estado);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }
    
    /**
     * Cambia el estado de verificación de un negocio (solo admin)
     * @param id ID del negocio
     * @param verificado Nuevo estado de verificación
     * @return Mensaje de respuesta
     */
    @PatchMapping("/{id}/verificacion")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> cambiarVerificacion(@PathVariable Long id, @RequestParam boolean verificado) {
        MensajeResponse respuesta = negocioService.cambiarVerificacion(id, verificado);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }
    
    /**
     * Elimina un negocio (solo admin)
     * @param id ID del negocio
     * @return Mensaje de respuesta
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> eliminar(@PathVariable Long id) {
        MensajeResponse respuesta = negocioService.eliminarNegocio(id);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.NOT_FOUND);
        }
    }
}