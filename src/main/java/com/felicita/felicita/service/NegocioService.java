package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.repository.NegocioRepository;
import com.felicita.felicita.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Servicio que gestiona las operaciones relacionadas con los negocios.
 */
@Service
public class NegocioService {

    @Autowired
    private NegocioRepository negocioRepository;
    
    @Autowired
    private UsuarioRepository usuarioRepository;
    
    /**
     * Obtiene todos los negocios
     * @return Lista de negocios
     */
    public List<Negocio> obtenerTodos() {
        return negocioRepository.findAll();
    }
    
    /**
     * Obtiene todos los negocios activos y verificados
     * @return Lista de negocios activos y verificados
     */
    public List<Negocio> obtenerNegociosActivos() {
        return negocioRepository.findByEstado("ACTIVO");
    }
    
    /**
     * Busca un negocio por su ID
     * @param id ID del negocio
     * @return Negocio si existe, vacío si no
     */
    public Optional<Negocio> obtenerPorId(Long id) {
        return negocioRepository.findById(id);
    }
    
    /**
     * Busca el negocio asociado a un usuario
     * @param usuarioId ID del usuario
     * @return Negocio si existe, vacío si no
     */
    public Optional<Negocio> obtenerPorUsuario(Long usuarioId) {
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
        if (usuarioOpt.isPresent()) {
            return negocioRepository.findByUsuario(usuarioOpt.get());
        }
        return Optional.empty();
    }
    
    /**
     * Crea un nuevo negocio
     * @param usuarioId ID del usuario que será propietario
     * @param negocio Datos del negocio a crear
     * @return Mensaje con el resultado de la operación
     */
    @Transactional
    public MensajeResponse crearNegocio(Long usuarioId, Negocio negocio) {
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
        
        if (usuarioOpt.isEmpty()) {
            return new MensajeResponse("Usuario no encontrado", false);
        }
        
        Usuario usuario = usuarioOpt.get();
        
        // Verificar si el usuario ya tiene un negocio asociado
        if (negocioRepository.findByUsuario(usuario).isPresent()) {
            return new MensajeResponse("El usuario ya tiene un negocio asociado", false);
        }
        
        // Cambiar el rol del usuario a PROADMIN
        usuario.setRol("PROADMIN");
        usuarioRepository.save(usuario);
        
        // Asociar usuario al negocio
        negocio.setUsuario(usuario);
        negocio.setEstado("ACTIVO");
        negocio.setVerificado(false); // Por defecto, requiere verificación
        
        negocioRepository.save(negocio);
        
        return new MensajeResponse("Negocio creado exitosamente", true);
    }
    
    /**
     * Actualiza los datos de un negocio
     * @param id ID del negocio
     * @param negocioDetalles Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarNegocio(Long id, Negocio negocioDetalles) {
        return negocioRepository.findById(id)
            .map(negocio -> {
                negocio.setNombreComercial(negocioDetalles.getNombreComercial());
                negocio.setDescripcion(negocioDetalles.getDescripcion());
                negocio.setDireccion(negocioDetalles.getDireccion());
                negocio.setTelefono(negocioDetalles.getTelefono());
                negocio.setCorreoContacto(negocioDetalles.getCorreoContacto());
                negocio.setLogo(negocioDetalles.getLogo());
                negocio.setHorarioOperacion(negocioDetalles.getHorarioOperacion());
                negocio.setTipo(negocioDetalles.getTipo());
                negocio.setLatitud(negocioDetalles.getLatitud());
                negocio.setLongitud(negocioDetalles.getLongitud());
                negocio.setSitioWeb(negocioDetalles.getSitioWeb());
                negocio.setRedesSociales(negocioDetalles.getRedesSociales());
                
                negocioRepository.save(negocio);
                return new MensajeResponse("Negocio actualizado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el negocio con ID: " + id, false));
    }
    
    /**
     * Cambia el estado de un negocio
     * @param id ID del negocio
     * @param estado Nuevo estado (ACTIVO, SUSPENDIDO, INACTIVO)
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarEstado(Long id, String estado) {
        if (!estado.equals("ACTIVO") && !estado.equals("SUSPENDIDO") && !estado.equals("INACTIVO")) {
            return new MensajeResponse("Estado no válido. Debe ser ACTIVO, SUSPENDIDO o INACTIVO", false);
        }
        
        return negocioRepository.findById(id)
            .map(negocio -> {
                negocio.setEstado(estado);
                negocioRepository.save(negocio);
                return new MensajeResponse("Estado del negocio actualizado a " + estado, true);
            })
            .orElse(new MensajeResponse("No se encontró el negocio con ID: " + id, false));
    }
    
    /**
     * Cambia el estado de verificación de un negocio
     * @param id ID del negocio
     * @param verificado Nuevo estado de verificación
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarVerificacion(Long id, boolean verificado) {
        return negocioRepository.findById(id)
            .map(negocio -> {
                negocio.setVerificado(verificado);
                negocioRepository.save(negocio);
                String mensaje = verificado ? 
                    "Negocio verificado exitosamente" : 
                    "Verificación del negocio revocada";
                return new MensajeResponse(mensaje, true);
            })
            .orElse(new MensajeResponse("No se encontró el negocio con ID: " + id, false));
    }
    
    /**
     * Busca negocios por nombre
     * @param nombre Texto a buscar en el nombre
     * @return Lista de negocios que coinciden
     */
    public List<Negocio> buscarPorNombre(String nombre) {
        return negocioRepository.findByNombreComercialContainingAndEstado(nombre, "ACTIVO");
    }
    
    /**
     * Busca negocios por tipo
     * @param tipo Tipo de negocio (SALON, BARBERIA, AMBOS)
     * @return Lista de negocios del tipo especificado
     */
    public List<Negocio> buscarPorTipo(String tipo) {
        return negocioRepository.findByTipo(tipo);
    }
    
    /**
     * Busca negocios cercanos a una ubicación
     * @param latitud Latitud del punto central
     * @param longitud Longitud del punto central
     * @param distanciaKm Distancia máxima en kilómetros
     * @return Lista de negocios cercanos
     */
    public List<Negocio> buscarNegociosCercanos(Double latitud, Double longitud, Double distanciaKm) {
        try {
            return negocioRepository.findNegociosCercanos(latitud, longitud, distanciaKm);
        } catch (Exception e) {
            System.err.println("Error al buscar negocios cercanos: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Elimina un negocio del sistema
     * @param id ID del negocio a eliminar
     * @return Mensaje con el resultado de la operación
     */
    @Transactional
    public MensajeResponse eliminarNegocio(Long id) {
        return negocioRepository.findById(id)
            .map(negocio -> {
                // En lugar de eliminar, marcamos como inactivo
                negocio.setEstado("INACTIVO");
                negocioRepository.save(negocio);
                
                // También actualizamos el rol del usuario si ya no tiene otro negocio activo
                Usuario usuario = negocio.getUsuario();
                usuario.setRol("CLIENTE");
                usuarioRepository.save(usuario);
                
                return new MensajeResponse("Negocio eliminado exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró el negocio con ID: " + id, false));
    }
}