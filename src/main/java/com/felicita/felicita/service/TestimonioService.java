package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Testimonio;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.repository.TestimonioRepository;
import com.felicita.felicita.repository.UsuarioRepository;
import com.felicita.felicita.repository.ServicioRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Servicio que gestiona las operaciones relacionadas con los testimonios.
 */
@Service
public class TestimonioService {

    @Autowired
    private TestimonioRepository testimonioRepository;
    
    @Autowired
    private UsuarioRepository usuarioRepository;
    
    @Autowired
    private ServicioRepository servicioRepository;
    
    /**
     * Obtiene todos los testimonios
     * @return Lista de testimonios
     */
    public List<Testimonio> obtenerTodos() {
        return testimonioRepository.findAll();
    }
    
    /**
     * Obtiene testimonios activos
     * @return Lista de testimonios activos
     */
    public List<Testimonio> obtenerActivos() {
        return testimonioRepository.findByActivoTrue();
    }
    
    /**
     * Obtiene un testimonio por su ID
     * @param id ID del testimonio
     * @return Testimonio si existe, vacío si no
     */
    public Optional<Testimonio> obtenerPorId(Long id) {
        return testimonioRepository.findById(id);
    }
    
    /**
     * Obtiene testimonios destacados para mostrar en la web
     * @return Lista de testimonios destacados
     */
    public List<Testimonio> obtenerTestimoniosDestacados() {
        try {
            // Obtener testimonios con mejores valoraciones (5 estrellas primero)
            return testimonioRepository.findTopTestimoniosByValoracion(6);
        } catch (Exception e) {
            System.err.println("Error al obtener testimonios destacados: " + e.getMessage());
            return new ArrayList<>(); // Devolver lista vacía en caso de error
        }
    }
    
    /**
     * Obtiene testimonios recientes
     * @param limite Límite de testimonios a retornar
     * @return Lista de testimonios recientes
     */
    public List<Testimonio> obtenerTestimoniosRecientes(int limite) {
        try {
            return testimonioRepository.findTopTestimoniosByFecha(limite);
        } catch (Exception e) {
            System.err.println("Error al obtener testimonios recientes: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Obtiene testimonios por usuario
     * @param usuarioId ID del usuario
     * @return Lista de testimonios del usuario
     */
    public List<Testimonio> obtenerPorUsuario(Long usuarioId) {
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
        if (usuarioOpt.isPresent()) {
            return testimonioRepository.findByUsuario(usuarioOpt.get());
        }
        return new ArrayList<>();
    }
    
    /**
     * Obtiene testimonios por servicio
     * @param servicioId ID del servicio
     * @return Lista de testimonios del servicio
     */
    public List<Testimonio> obtenerPorServicio(Long servicioId) {
        Optional<Servicio> servicioOpt = servicioRepository.findById(servicioId);
        if (servicioOpt.isPresent()) {
            return testimonioRepository.findByServicio(servicioOpt.get());
        }
        return new ArrayList<>();
    }
    
    /**
     * Crea un nuevo testimonio
     * @param usuarioId ID del usuario que crea el testimonio
     * @param servicioId ID del servicio asociado
     * @param testimonio Datos del testimonio
     * @return Mensaje con el resultado de la operación
     */
    @Transactional
    public MensajeResponse crearTestimonio(Long usuarioId, Long servicioId, Testimonio testimonio) {
        try {
            // Validaciones básicas
            if (testimonio.getMensaje() == null || testimonio.getMensaje().trim().isEmpty()) {
                return new MensajeResponse("El mensaje no puede estar vacío", false);
            }
            
            if (testimonio.getValoracion() == null || testimonio.getValoracion() < 1 || testimonio.getValoracion() > 5) {
                return new MensajeResponse("La valoración debe estar entre 1 y 5", false);
            }
            
            // Buscar usuario y servicio
            Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
            Optional<Servicio> servicioOpt = servicioRepository.findById(servicioId);
            
            if (usuarioOpt.isEmpty()) {
                return new MensajeResponse("Usuario no encontrado", false);
            }
            
            if (servicioOpt.isEmpty()) {
                return new MensajeResponse("Servicio no encontrado", false);
            }
            
            // Crear el testimonio
            testimonio.setUsuario(usuarioOpt.get());
            testimonio.setServicio(servicioOpt.get());
            testimonio.setNombreCliente(usuarioOpt.get().getNombreCompleto()); // Usar nombre del usuario
            
            // Por defecto los testimonios no están activos hasta revisión
            testimonio.setActivo(false);
            
            testimonioRepository.save(testimonio);
            
            return new MensajeResponse("Testimonio enviado correctamente. Será revisado antes de publicarse.", true);
            
        } catch (Exception e) {
            return new MensajeResponse("Error al crear testimonio: " + e.getMessage(), false);
        }
    }
    
    /**
     * Aprueba un testimonio para hacerlo visible
     * @param id ID del testimonio
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse aprobarTestimonio(Long id) {
        return testimonioRepository.findById(id)
            .map(testimonio -> {
                testimonio.setActivo(true);
                testimonioRepository.save(testimonio);
                return new MensajeResponse("Testimonio aprobado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el testimonio con ID: " + id, false));
    }
    
    /**
     * Rechaza un testimonio para que no sea visible
     * @param id ID del testimonio
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse rechazarTestimonio(Long id) {
        return testimonioRepository.findById(id)
            .map(testimonio -> {
                testimonio.setActivo(false);
                testimonioRepository.save(testimonio);
                return new MensajeResponse("Testimonio rechazado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el testimonio con ID: " + id, false));
    }
    
    /**
     * Elimina un testimonio
     * @param id ID del testimonio a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarTestimonio(Long id) {
        return testimonioRepository.findById(id)
            .map(testimonio -> {
                testimonioRepository.delete(testimonio);
                return new MensajeResponse("Testimonio eliminado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el testimonio con ID: " + id, false));
    }
    
    /**
     * Obtiene estadísticas de valoraciones de un servicio
     * @param servicioId ID del servicio
     * @return Mapa con las estadísticas
     */
    public Map<String, Object> obtenerEstadisticasServicio(Long servicioId) {
        Map<String, Object> estadisticas = new HashMap<>();
        
        try {
            // Valoración promedio
            Double promedio = testimonioRepository.calcularValoracionPromedioPorServicio(servicioId);
            estadisticas.put("promedio", promedio != null ? promedio : 0);
            
            // Contador por cada valoración
            Map<Integer, Long> contadores = new HashMap<>();
            for (int i = 1; i <= 5; i++) {
                Long cantidad = testimonioRepository.countByServicioIdAndValoracionAndActivoTrue(servicioId, i);
                contadores.put(i, cantidad);
            }
            estadisticas.put("distribución", contadores);
            
            // Total de testimonios
            long total = contadores.values().stream().mapToLong(Long::longValue).sum();
            estadisticas.put("total", total);
            
        } catch (Exception e) {
            System.err.println("Error al obtener estadísticas: " + e.getMessage());
        }
        
        return estadisticas;
    }
}