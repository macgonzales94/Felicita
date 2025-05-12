package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.ServicioReserva;
import com.felicita.felicita.repository.ServicioRepository;
import com.felicita.felicita.repository.ServicioReservaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;

/**
 * Servicio que gestiona las operaciones relacionadas con los servicios
 * ofrecidos.
 */
@Service
public class ServicioService {

    @Autowired
    private ServicioRepository servicioRepository;
    
    @Autowired
    private ServicioReservaRepository servicioReservaRepository;

    /**
     * Obtiene todos los servicios
     * 
     * @return Lista de servicios
     */
    public List<Servicio> obtenerTodos() {
        return servicioRepository.findAll();
    }

    /**
     * Obtiene todos los servicios activos
     * 
     * @return Lista de servicios activos
     */
    public List<Servicio> obtenerTodosActivos() {
        try {
            List<Servicio> servicios = servicioRepository.findByActivoTrue();
            System.out.println("Servicios activos encontrados: " + servicios.size());
            if (servicios.isEmpty()) {
                System.out.println("No se encontraron servicios activos en la base de datos");
            } else {
                System.out.println("Primer servicio: " + servicios.get(0).getNombre());
            }
            return servicios;
        } catch (Exception e) {
            System.err.println("Error en obtenerTodosActivos: " + e.toString());
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    /**
     * Busca servicios por nombre
     * 
     * @param nombre Nombre a buscar
     * @return Lista de servicios que coinciden
     */
    public List<Servicio> buscarPorNombre(String nombre) {
        return servicioRepository.findByNombreContaining(nombre);
    }

    /**
     * Busca un servicio por su ID
     * 
     * @param id ID del servicio
     * @return Servicio si existe, vacío si no
     */
    public Optional<Servicio> obtenerPorId(Long id) {
        return servicioRepository.findById(id);
    }

    /**
     * Crea un nuevo servicio
     * 
     * @param servicio Datos del servicio a crear
     * @return Servicio creado
     */
    public Servicio crearServicio(Servicio servicio) {
        return servicioRepository.save(servicio);
    }

    /**
     * Actualiza un servicio existente
     * 
     * @param id               ID del servicio a actualizar
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
     * 
     * @param id     ID del servicio
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
     * 
     * @param id ID del servicio a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarServicio(Long id) {
        return servicioRepository.findById(id)
                .map(servicio -> {
                    // En lugar de eliminar, desactivamos el servicio para mantener integridad
                    // referencial
                    servicio.setActivo(false);
                    servicioRepository.save(servicio);
                    return new MensajeResponse("Servicio eliminado exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró el servicio con ID: " + id, false));
    }
    
    /**
     * Obtiene los servicios más populares basados en la cantidad de reservas
     * 
     * @param limite Número máximo de servicios a retornar
     * @return Lista de servicios más populares
     */
    public List<Servicio> obtenerServiciosMasPopulares(int limite) {
        try {
            // Obtener todas las relaciones servicio-reserva
            List<ServicioReserva> todasRelaciones = servicioReservaRepository.findAll();
            
            // Contar frecuencia de cada servicio y crear mapa
            Map<Servicio, Long> frecuenciaServicios = new HashMap<>();
            
            for (ServicioReserva sr : todasRelaciones) {
                Servicio servicio = sr.getServicio();
                
                // Solo considerar servicios activos
                if (servicio.isActivo()) {
                    frecuenciaServicios.put(servicio, 
                        frecuenciaServicios.getOrDefault(servicio, 0L) + 1);
                }
            }
            
            // Ordenar por frecuencia descendente y limitar
            return frecuenciaServicios.entrySet().stream()
                .sorted(Map.Entry.<Servicio, Long>comparingByValue().reversed())
                .limit(limite)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
            
        } catch (Exception e) {
            System.err.println("Error al obtener servicios populares: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Busca servicios por rango de precio
     * 
     * @param precioMin Precio mínimo
     * @param precioMax Precio máximo
     * @return Lista de servicios dentro del rango de precio
     */
    public List<Servicio> buscarPorRangoPrecio(Double precioMin, Double precioMax) {
        try {
            return servicioRepository.findByPrecioBetween(precioMin, precioMax);
        } catch (Exception e) {
            System.err.println("Error al buscar por rango de precio: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Busca servicios con duración menor o igual a un valor dado
     * 
     * @param duracionMaxima Duración máxima en minutos
     * @return Lista de servicios con duración menor o igual
     */
    public List<Servicio> buscarPorDuracionMaxima(Integer duracionMaxima) {
        try {
            return servicioRepository.findByDuracionLessThanEqual(duracionMaxima);
        } catch (Exception e) {
            System.err.println("Error al buscar por duración máxima: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Obtiene categorías disponibles de servicios
     * 
     * @return Lista de categorías
     */
    public List<String> obtenerCategorias() {
        // Nota: Esto debe actualizarse si se agrega campo categoria a la entidad Servicio
        List<String> categorias = new ArrayList<>();
        categorias.add("Cabello");
        categorias.add("Uñas");
        categorias.add("Facial");
        categorias.add("Barbería");
        categorias.add("Spa");
        
        return categorias;
    }
}