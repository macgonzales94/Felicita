package com.felicita.felicita.controller;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.service.ServicioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Controlador REST para operaciones relacionadas con servicios.
 */
@RestController
@RequestMapping("/api/servicios")
public class ServicioRestController {

    @Autowired
    private ServicioService servicioService;

    /**
     * Obtiene todos los servicios
     * @return Lista de servicios
     */
    @GetMapping
    public ResponseEntity<List<Servicio>> obtenerTodos() {
        List<Servicio> servicios = servicioService.obtenerTodos();
        return new ResponseEntity<>(servicios, HttpStatus.OK);
    }

    /**
     * Obtiene todos los servicios activos
     * @return Lista de servicios activos
     */
    @GetMapping("/activos")
    public ResponseEntity<List<Servicio>> obtenerActivos() {
        List<Servicio> serviciosActivos = servicioService.obtenerTodosActivos();
        return new ResponseEntity<>(serviciosActivos, HttpStatus.OK);
    }

    /**
     * Busca servicios por nombre
     * @param nombre Nombre a buscar
     * @return Lista de servicios que coinciden
     */
    @GetMapping("/buscar")
    public ResponseEntity<List<Servicio>> buscarPorNombre(@RequestParam String nombre) {
        List<Servicio> servicios = servicioService.buscarPorNombre(nombre);
        return new ResponseEntity<>(servicios, HttpStatus.OK);
    }

    /**
     * Obtiene un servicio por su ID
     * @param id ID del servicio
     * @return Servicio si existe
     */
    @GetMapping("/{id}")
    public ResponseEntity<Servicio> obtenerPorId(@PathVariable Long id) {
        return servicioService.obtenerPorId(id)
                .map(servicio -> new ResponseEntity<>(servicio, HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    /**
     * Crea un nuevo servicio (solo admin)
     * @param servicio Datos del servicio
     * @return Servicio creado
     */
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Servicio> crear(@Valid @RequestBody Servicio servicio) {
        Servicio nuevoServicio = servicioService.crearServicio(servicio);
        return new ResponseEntity<>(nuevoServicio, HttpStatus.CREATED);
    }

    /**
     * Actualiza un servicio (solo admin)
     * @param id ID del servicio
     * @param servicio Datos actualizados
     * @return Mensaje de respuesta
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> actualizar(@PathVariable Long id, @Valid @RequestBody Servicio servicio) {
        MensajeResponse respuesta = servicioService.actualizarServicio(id, servicio);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }

    /**
     * Cambia el estado de activación de un servicio (solo admin)
     * @param id ID del servicio
     * @param activo Nuevo estado
     * @return Mensaje de respuesta
     */
    @PatchMapping("/{id}/estado")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> cambiarEstado(@PathVariable Long id, @RequestParam boolean activo) {
        MensajeResponse respuesta = servicioService.cambiarEstadoActivacion(id, activo);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.BAD_REQUEST);
        }
    }

    /**
     * Elimina un servicio (solo admin)
     * @param id ID del servicio
     * @return Mensaje de respuesta
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<MensajeResponse> eliminar(@PathVariable Long id) {
        MensajeResponse respuesta = servicioService.eliminarServicio(id);
        
        if (respuesta.isExito()) {
            return new ResponseEntity<>(respuesta, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(respuesta, HttpStatus.NOT_FOUND);
        }
    }
}