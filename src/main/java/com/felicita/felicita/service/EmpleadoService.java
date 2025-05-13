package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Disponibilidad;
import com.felicita.felicita.model.Empleado;
import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.repository.DisponibilidadRepository;
import com.felicita.felicita.repository.EmpleadoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Servicio que gestiona las operaciones relacionadas con los empleados.
 */
@Service
public class EmpleadoService {

    @Autowired
    private EmpleadoRepository empleadoRepository;

    @Autowired
    private DisponibilidadRepository disponibilidadRepository;

    /**
     * Obtiene todos los empleados
     * 
     * @return Lista de empleados
     */
    public List<Empleado> obtenerTodos() {
        return empleadoRepository.findAll();
    }

    /**
     * Obtiene todos los empleados activos
     * 
     * @return Lista de empleados activos
     */
    public List<Empleado> obtenerTodosActivos() {
        return empleadoRepository.findByActivoTrue();
    }

    /**
     * Busca empleados por cargo
     * 
     * @param cargo Cargo a buscar
     * @return Lista de empleados con ese cargo
     */
    public List<Empleado> buscarPorCargo(String cargo) {
        return empleadoRepository.findByCargo(cargo);
    }

    /**
     * Busca un empleado por su ID
     * 
     * @param id ID del empleado
     * @return Empleado si existe, vacío si no
     */
    public Optional<Empleado> obtenerPorId(Long id) {
        return empleadoRepository.findById(id);
    }

    /**
     * Crea un nuevo empleado
     * 
     * @param empleado Datos del empleado a crear
     * @return Empleado creado
     */
    public Empleado crearEmpleado(Empleado empleado) {
        return empleadoRepository.save(empleado);
    }

    /**
     * Actualiza un empleado existente
     * 
     * @param id               ID del empleado a actualizar
     * @param empleadoDetalles Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarEmpleado(Long id, Empleado empleadoDetalles) {
        return empleadoRepository.findById(id)
                .map(empleado -> {
                    empleado.setNombre(empleadoDetalles.getNombre());
                    empleado.setCargo(empleadoDetalles.getCargo());
                    empleado.setFoto(empleadoDetalles.getFoto());

                    empleadoRepository.save(empleado);
                    return new MensajeResponse("Empleado actualizado exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró el empleado con ID: " + id, false));
    }

    /**
     * Cambia el estado de activación de un empleado
     * 
     * @param id     ID del empleado
     * @param activo Nuevo estado
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarEstadoActivacion(Long id, boolean activo) {
        return empleadoRepository.findById(id)
                .map(empleado -> {
                    empleado.setActivo(activo);
                    empleadoRepository.save(empleado);
                    String mensaje = activo ? "Empleado activado exitosamente" : "Empleado desactivado exitosamente";
                    return new MensajeResponse(mensaje, true);
                })
                .orElse(new MensajeResponse("No se encontró el empleado con ID: " + id, false));
    }

    /**
     * Obtiene la disponibilidad de un empleado para una fecha específica
     * 
     * @param empleadoId ID del empleado
     * @param fecha      Fecha a consultar
     * @return Lista de disponibilidades
     */
    public List<Disponibilidad> obtenerDisponibilidadPorFecha(Long empleadoId, LocalDate fecha) {
        Optional<Empleado> empleadoOpt = empleadoRepository.findById(empleadoId);
        if (empleadoOpt.isPresent()) {
            return disponibilidadRepository.findByEmpleadoAndDia(empleadoOpt.get(), fecha);
        }
        return List.of();
    }

    /**
     * Agrega una nueva disponibilidad a un empleado
     * 
     * @param empleadoId     ID del empleado
     * @param disponibilidad Datos de disponibilidad
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse agregarDisponibilidad(Long empleadoId, Disponibilidad disponibilidad) {
        return empleadoRepository.findById(empleadoId)
                .map(empleado -> {
                    disponibilidad.setEmpleado(empleado);
                    disponibilidadRepository.save(disponibilidad);
                    return new MensajeResponse("Disponibilidad agregada exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró el empleado con ID: " + empleadoId, false));
    }

    /**
     * Actualiza una disponibilidad existente
     * 
     * @param disponibilidadId ID de la disponibilidad
     * @param detalles         Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarDisponibilidad(Long disponibilidadId, Disponibilidad detalles) {
        return disponibilidadRepository.findById(disponibilidadId)
                .map(disponibilidad -> {
                    disponibilidad.setDia(detalles.getDia());
                    disponibilidad.setHoraInicio(detalles.getHoraInicio());
                    disponibilidad.setHoraFin(detalles.getHoraFin());
                    disponibilidad.setDisponible(detalles.isDisponible());

                    disponibilidadRepository.save(disponibilidad);
                    return new MensajeResponse("Disponibilidad actualizada exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró la disponibilidad con ID: " + disponibilidadId, false));
    }

    /**
     * Elimina una disponibilidad
     * 
     * @param disponibilidadId ID de la disponibilidad a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarDisponibilidad(Long disponibilidadId) {
        return disponibilidadRepository.findById(disponibilidadId)
                .map(disponibilidad -> {
                    disponibilidadRepository.delete(disponibilidad);
                    return new MensajeResponse("Disponibilidad eliminada exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró la disponibilidad con ID: " + disponibilidadId, false));
    }

    /**
     * Busca empleados por cargo
     * 
     * @param cargo Cargo a buscar
     * @return Lista de empleados con ese cargo
     */
    public List<Empleado> obtenerPorCargo(String cargo) {
        return empleadoRepository.findByCargo(cargo);
    }

 /**
 * Obtiene empleados por negocio
 * @param negocioId ID del negocio
 * @return Lista de empleados del negocio
 */
public List<Empleado> obtenerPorNegocio(Long negocioId) {
    Optional<Negocio> negocio = negocioRepository.findById(negocioId);
    if (negocio.isPresent()) {
        return empleadoRepository.findByNegocio(negocio.get());
    }
    return new ArrayList<>();
}

public Empleado crear(Empleado empleado) {
    // Valida datos
    if (empleado.getNombre() == null || empleado.getNombre().isEmpty()) {
        throw new IllegalArgumentException("El nombre del empleado es obligatorio");
    }
    
    // Guarda y retorna
    return empleadoRepository.save(empleado);
}


}