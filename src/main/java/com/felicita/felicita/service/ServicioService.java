package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.repository.ServicioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Servicio que gestiona las operaciones relacionadas con los servicios ofrecidos.
 */
@Service
public class ServicioService {

    @Autowired
    private ServicioRepository servicioRepository;
    
    /**
     * Obtiene todos los servicios
     * @return Lista de servicios
     */
    public List<Servicio> obtenerTodos() {
        return servicioRepository.findAll();
    }
    
    /**
     * Obtiene todos los servicios activos
     * @return Lista de servicios activos
     */
    public List<Servicio> obtenerTodosActivos() {
        return servicioRepository.findByActivoTrue();
    }
    
    /**
     * Busca servicios por nombre
     * @param nombre Nombre a buscar
     * @return Lista de servicios que coinciden
     */
    public List<Servicio> buscarPorNombre(String nombre) {
        return servicioRepository.findByNombreContaining(nombre);
    }
    
    /**
     * Busca un servicio por su ID
     * @param id ID del servicio
     * @return Servicio si existe, vacío si no
     */
    public Optional<Servicio> obtenerPorId(Long id) {
        return servicioRepository.findById(id);
    }
    
    /**
     * Crea un nuevo servicio
     * @param servicio Datos del servicio a crear
     * @return Servicio creado
     */
    public Servicio crearServicio(Servicio servicio) {
        return servicioRepository.save(servicio);
    }
    
    /**
     * Actualiza un servicio existente
     * @param id ID del servicio a actualizar
     * @param servicioDetalles Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarServicio(Long id, Servicio servicioDetalles) {
        return servicioRepository.findById(id)
            .map(servicio -> {
                servicio.setNombre(servicioDetalles.getNombre());
                servicio.setDescripcion(servicioDetalles.getDescripcion());
                servicio.setPrecio(servicioDetalles.getPrecio());
                servicio.setDuracion(servicioDetalles.getDuracion());
                servicio.setImagen(servicioDetalles.getImagen());
                
                servicioRepository.save(servicio);
                return new MensajeResponse("Servicio actualizado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el servicio con ID: " + id, false));
    }
    
    /**
     * Cambia el estado de activación de un servicio
     * @param id ID del servicio
     * @param activo Nuevo estado
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarEstadoActivacion(Long id, boolean activo) {
        return servicioRepository.findById(id)
            .map(servicio -> {
                servicio.setActivo(activo);
                servicioRepository.save(servicio);
                String mensaje = activo ? "Servicio activado exitosamente" : "Servicio desactivado exitosamente";
                return new MensajeResponse(mensaje, true);
            })
            .orElse(new MensajeResponse("No se encontró el servicio con ID: " + id, false));
    }
    
    /**
     * Elimina un servicio
     * @param id ID del servicio a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarServicio(Long id) {
        return servicioRepository.findById(id)
            .map(servicio -> {
                // En lugar de eliminar, desactivamos el servicio para mantener integridad referencial
                servicio.setActivo(false);
                servicioRepository.save(servicio);
                return new MensajeResponse("Servicio eliminado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el servicio con ID: " + id, false));
    }
}