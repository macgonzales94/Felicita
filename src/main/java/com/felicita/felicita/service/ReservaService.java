package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.*;
import com.felicita.felicita.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Servicio que gestiona las operaciones relacionadas con las reservas.
 */
@Service
public class ReservaService {

    @Autowired
    private ReservaRepository reservaRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private EmpleadoRepository empleadoRepository;

    @Autowired
    private ServicioRepository servicioRepository;

    @Autowired
    private ServicioReservaRepository servicioReservaRepository;

    @Autowired
    private DisponibilidadRepository disponibilidadRepository;

    /**
     * Obtiene todas las reservas
     * 
     * @return Lista de reservas
     */
    public List<Reserva> obtenerTodas() {
        return reservaRepository.findAll();
    }

    /**
     * Busca reservas por estado
     * 
     * @param estado Estado de la reserva
     * @return Lista de reservas con ese estado
     */
    public List<Reserva> buscarPorEstado(Reserva.EstadoReserva estado) {
        return reservaRepository.findByEstado(estado);
    }

    /**
     * Busca reservas para un período específico
     * 
     * @param inicio Fecha y hora de inicio
     * @param fin    Fecha y hora de fin
     * @return Lista de reservas en ese período
     */
    public List<Reserva> buscarPorPeriodo(LocalDateTime inicio, LocalDateTime fin) {
        return reservaRepository.findByHoraInicioBetween(inicio, fin);
    }

    /**
     * Busca reservas de un usuario específico
     * 
     * @param usuarioId ID del usuario
     * @return Lista de reservas del usuario
     */
    public List<Reserva> buscarPorUsuario(Long usuarioId) {
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
        if (usuarioOpt.isPresent()) {
            return reservaRepository.findByUsuario(usuarioOpt.get());
        }
        return new ArrayList<>();
    }

    /**
     * Busca reservas asignadas a un empleado específico
     * 
     * @param empleadoId ID del empleado
     * @return Lista de reservas del empleado
     */
    public List<Reserva> buscarPorEmpleado(Long empleadoId) {
        Optional<Empleado> empleadoOpt = empleadoRepository.findById(empleadoId);
        if (empleadoOpt.isPresent()) {
            return reservaRepository.findByEmpleado(empleadoOpt.get());
        }
        return new ArrayList<>();
    }

    /**
     * Busca una reserva por su ID
     * 
     * @param id ID de la reserva
     * @return Reserva si existe, vacío si no
     */
    public Optional<Reserva> obtenerPorId(Long id) {
        return reservaRepository.findById(id);
    }

    /**
     * Verifica si un horario está disponible para reservar
     * 
     * @param empleadoId ID del empleado
     * @param fecha      Fecha de la reserva
     * @param horaInicio Hora de inicio
     * @param horaFin    Hora de fin
     * @return true si está disponible, false si no
     */
    public boolean verificarDisponibilidad(Long empleadoId, LocalDate fecha, LocalTime horaInicio, LocalTime horaFin) {
        // Verificar disponibilidad del empleado
        Optional<Empleado> empleadoOpt = empleadoRepository.findById(empleadoId);
        if (empleadoOpt.isEmpty()) {
            return false;
        }

        Empleado empleado = empleadoOpt.get();

        // Verificar si el empleado tiene horario para esa fecha
        List<Disponibilidad> disponibilidades = disponibilidadRepository.findByEmpleadoAndDia(empleado, fecha);
        if (disponibilidades.isEmpty()) {
            return false;
        }

        // Verificar si el horario está dentro de la disponibilidad
        boolean horarioDisponible = disponibilidades.stream()
                .anyMatch(d -> d.isDisponible() &&
                        !horaInicio.isBefore(d.getHoraInicio()) &&
                        !horaFin.isAfter(d.getHoraFin()));

        if (!horarioDisponible) {
            return false;
        }

        // Verificar si no hay reservas que se solapen
        LocalDateTime inicioReserva = LocalDateTime.of(fecha, horaInicio);
        LocalDateTime finReserva = LocalDateTime.of(fecha, horaFin);

        List<Reserva> reservasExistentes = reservaRepository.findByEmpleado(empleado);

        return reservasExistentes.stream()
                .filter(r -> r.getEstado() != Reserva.EstadoReserva.CANCELADA)
                .noneMatch(r -> {
                    // Verificar si hay solapamiento
                    return (inicioReserva.isBefore(r.getHoraFin()) && finReserva.isAfter(r.getHoraInicio()));
                });
    }

    /**
     * Crea una nueva reserva
     * 
     * @param usuarioId    ID del usuario que realiza la reserva
     * @param empleadoId   ID del empleado asignado
     * @param serviciosIds IDs de los servicios incluidos
     * @param fecha        Fecha de la reserva
     * @param horaInicio   Hora de inicio
     * @param notas        Notas adicionales
     * @return Mensaje con el resultado de la operación
     */
    @Transactional
    public MensajeResponse crearReserva(Long usuarioId, Long empleadoId, List<Long> serviciosIds,
            LocalDate fecha, LocalTime horaInicio, String notas) {
        // Obtener usuario
        Optional<Usuario> usuarioOpt = usuarioRepository.findById(usuarioId);
        if (usuarioOpt.isEmpty()) {
            return new MensajeResponse("Usuario no encontrado", false);
        }

        // Obtener empleado
        Optional<Empleado> empleadoOpt = empleadoRepository.findById(empleadoId);
        if (empleadoOpt.isEmpty()) {
            return new MensajeResponse("Empleado no encontrado", false);
        }

        // Obtener servicios
        List<Servicio> servicios = servicioRepository.findAllById(serviciosIds);
        if (servicios.isEmpty() || servicios.size() != serviciosIds.size()) {
            return new MensajeResponse("Uno o más servicios no encontrados", false);
        }

        // Calcular duración total
        int duracionTotal = servicios.stream().mapToInt(Servicio::getDuracion).sum();
        LocalTime horaFin = horaInicio.plusMinutes(duracionTotal);

        // Verificar disponibilidad
        if (!verificarDisponibilidad(empleadoId, fecha, horaInicio, horaFin)) {
            return new MensajeResponse("Horario no disponible", false);
        }

        // Crear reserva
        Reserva reserva = new Reserva();
        reserva.setUsuario(usuarioOpt.get());
        reserva.setEmpleado(empleadoOpt.get());
        reserva.setHoraInicio(LocalDateTime.of(fecha, horaInicio));
        reserva.setHoraFin(LocalDateTime.of(fecha, horaFin));
        reserva.setEstado(Reserva.EstadoReserva.PENDIENTE);
        reserva.setNotas(notas);

        // Guardar reserva
        Reserva reservaGuardada = reservaRepository.save(reserva);

        // Asociar servicios
        for (Servicio servicio : servicios) {
            ServicioReserva servicioReserva = new ServicioReserva(reservaGuardada, servicio);
            servicioReservaRepository.save(servicioReserva);
        }

        return new MensajeResponse("Reserva creada exitosamente", true);
    }

    /**
     * Actualiza el estado de una reserva
     * 
     * @param id          ID de la reserva
     * @param nuevoEstado Nuevo estado
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarEstado(Long id, Reserva.EstadoReserva nuevoEstado) {
        return reservaRepository.findById(id)
                .map(reserva -> {
                    reserva.setEstado(nuevoEstado);
                    reservaRepository.save(reserva);
                    return new MensajeResponse("Estado de reserva actualizado exitosamente", true);
                })
                .orElse(new MensajeResponse("No se encontró la reserva con ID: " + id, false));
    }

    /**
     * Cancela una reserva
     * 
     * @param id ID de la reserva
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cancelarReserva(Long id) {
        return actualizarEstado(id, Reserva.EstadoReserva.CANCELADA);
    }

    /**
     * Confirma una reserva
     * 
     * @param id ID de la reserva
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse confirmarReserva(Long id) {
        return actualizarEstado(id, Reserva.EstadoReserva.CONFIRMADA);
    }

    /**
     * Marca una reserva como completada
     * 
     * @param id ID de la reserva
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse completarReserva(Long id) {
        return actualizarEstado(id, Reserva.EstadoReserva.COMPLETADA);
    }

    /**
     * Obtiene los servicios incluidos en una reserva
     * 
     * @param reservaId ID de la reserva
     * @return Lista de servicios
     */
    public List<Servicio> obtenerServiciosPorReserva(Long reservaId) {
        Optional<Reserva> reservaOpt = reservaRepository.findById(reservaId);
        if (reservaOpt.isPresent()) {
            List<ServicioReserva> serviciosReservas = servicioReservaRepository.findByReserva(reservaOpt.get());
            return serviciosReservas.stream()
                    .map(ServicioReserva::getServicio)
                    .collect(Collectors.toList());
        }
        return new ArrayList<>();
    }

    /**
     * Busca reservas por negocio
     * 
     * @param negocioId ID del negocio
     * @return Lista de reservas del negocio
     */
    public List<Reserva> buscarPorNegocio(Long negocioId) {
        List<Reserva> todasReservas = reservaRepository.findAll();

        // Filtrar reservas que pertenecen al negocio a través de los empleados
        return todasReservas.stream()
                .filter(r -> r.getEmpleado() != null &&
                        r.getEmpleado().getNegocio() != null &&
                        r.getEmpleado().getNegocio().getId().equals(negocioId))
                .collect(Collectors.toList());
    }

    /**
     * Busca reservas recientes por negocio
     * 
     * @param negocioId ID del negocio
     * @param limite    Cantidad máxima de reservas a retornar
     * @return Lista de reservas recientes del negocio
     */
    public List<Reserva> buscarReservasRecientesPorNegocio(Long negocioId, int limite) {
        List<Reserva> reservasNegocio = buscarPorNegocio(negocioId);

        // Ordenar por fecha de creación descendente y limitar
        return reservasNegocio.stream()
                .sorted(Comparator.comparing(Reserva::getFechaCreacion).reversed())
                .limit(limite)
                .collect(Collectors.toList());
    }

    /**
     * Calcula ingresos para un periodo de tiempo específico para un negocio
     * 
     * @param negocioId ID del negocio
     * @param inicio    Fecha y hora de inicio del periodo
     * @param fin       Fecha y hora de fin del periodo
     * @return Total de ingresos para el periodo
     */
    public BigDecimal calcularIngresosPorPeriodoYNegocio(Long negocioId, LocalDateTime inicio, LocalDateTime fin) {
        // Obtener reservas en el periodo
        List<Reserva> reservasEnPeriodo = reservaRepository.findByHoraInicioBetween(inicio, fin);

        // Filtrar por negocio y estado (COMPLETADA o CONFIRMADA)
        return reservasEnPeriodo.stream()
                .filter(r -> r.getEmpleado() != null &&
                        r.getEmpleado().getNegocio() != null &&
                        r.getEmpleado().getNegocio().getId().equals(negocioId) &&
                        (r.getEstado() == Reserva.EstadoReserva.COMPLETADA ||
                                r.getEstado() == Reserva.EstadoReserva.CONFIRMADA))
                .flatMap(r -> servicioReservaRepository.findByReserva(r).stream())
                .map(sr -> sr.getServicio().getPrecio())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    /**
     * Obtiene estadísticas de reservas por estado para un negocio
     * 
     * @param negocioId ID del negocio
     * @return Mapa con contadores por estado
     */
    public Map<Reserva.EstadoReserva, Long> obtenerEstadisticasReservasPorNegocio(Long negocioId) {
        List<Reserva> reservasNegocio = buscarPorNegocio(negocioId);

        return reservasNegocio.stream()
                .collect(Collectors.groupingBy(Reserva::getEstado, Collectors.counting()));
    }


    public List<Reserva> obtenerPorNegocio(Negocio negocio) {
        List<Empleado> empleados = empleadoRepository.findByNegocio(negocio);
        return reservaRepository.findByEmpleadoIn(empleados);
    }
    
    public List<Reserva> obtenerReservasRecientesPorNegocio(Negocio negocio, int limite) {
        List<Reserva> todasReservas = obtenerPorNegocio(negocio);
        return todasReservas.stream()
            .sorted(Comparator.comparing(Reserva::getFechaCreacion).reversed())
            .limit(limite)
            .collect(Collectors.toList());
    }
    
    public BigDecimal calcularIngresosPorPeriodo(Negocio negocio, LocalDateTime inicio, LocalDateTime fin) {
        List<Reserva> reservas = obtenerPorNegocio(negocio);
        
        return reservas.stream()
            .filter(r -> r.getHoraInicio().isAfter(inicio) && r.getHoraInicio().isBefore(fin))
            .filter(r -> r.getEstado() == Reserva.EstadoReserva.COMPLETADA || r.getEstado() == Reserva.EstadoReserva.CONFIRMADA)
            .flatMap(r -> r.getServiciosReservas().stream())
            .map(sr -> sr.getServicio().getPrecio())
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
    
    public Reserva actualizar(Reserva reserva) {
        return reservaRepository.save(reserva);
    }
}