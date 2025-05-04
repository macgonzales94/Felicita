package com.felicita.felicita.service;

import com.felicita.felicita.model.Reserva;
import com.felicita.felicita.model.Servicio;
import com.felicita.felicita.model.ServicioReserva;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.repository.ReservaRepository;
import com.felicita.felicita.repository.ServicioReservaRepository;
import com.felicita.felicita.repository.ServicioRepository;
import com.felicita.felicita.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Servicio que proporciona estadísticas y métricas para el dashboard administrativo.
 */
@Service
public class DashboardService {

    @Autowired
    private ReservaRepository reservaRepository;
    
    @Autowired
    private UsuarioRepository usuarioRepository;
    
    @Autowired
    private ServicioRepository servicioRepository;
    
    @Autowired
    private ServicioReservaRepository servicioReservaRepository;
    
    /**
     * Obtiene el total de reservas para un período
     * @param inicio Fecha y hora de inicio
     * @param fin Fecha y hora de fin
     * @return Total de reservas
     */
    public long obtenerTotalReservas(LocalDateTime inicio, LocalDateTime fin) {
        List<Reserva> reservas = reservaRepository.findByHoraInicioBetween(inicio, fin);
        return reservas.size();
    }
    
    /**
     * Obtiene el total de clientes registrados
     * @return Total de clientes
     */
    public long obtenerTotalClientes() {
        return usuarioRepository.count();
    }
    
    /**
     * Obtiene el total de servicios activos
     * @return Total de servicios activos
     */
    public long obtenerTotalServiciosActivos() {
        List<Servicio> serviciosActivos = servicioRepository.findByActivoTrue();
        return serviciosActivos.size();
    }
    
    /**
     * Calcula los ingresos totales para un período
     * @param inicio Fecha y hora de inicio
     * @param fin Fecha y hora de fin
     * @return Ingresos totales
     */
    public BigDecimal calcularIngresosTotales(LocalDateTime inicio, LocalDateTime fin) {
        List<Reserva> reservas = reservaRepository.findByHoraInicioBetween(inicio, fin);
        
        BigDecimal ingresosTotales = BigDecimal.ZERO;
        
        for (Reserva reserva : reservas) {
            if (reserva.getEstado() == Reserva.EstadoReserva.COMPLETADA || 
                reserva.getEstado() == Reserva.EstadoReserva.CONFIRMADA) {
                
                List<ServicioReserva> serviciosReserva = servicioReservaRepository.findByReserva(reserva);
                for (ServicioReserva sr : serviciosReserva) {
                    ingresosTotales = ingresosTotales.add(sr.getServicio().getPrecio());
                }
            }
        }
        
        return ingresosTotales;
    }
    
    /**
     * Obtiene las reservas recientes
     * @param limite Número máximo de reservas a retornar
     * @return Lista de reservas recientes
     */
    public List<Reserva> obtenerReservasRecientes(int limite) {
        List<Reserva> todasReservas = reservaRepository.findAll();
        
        // Ordenar por fecha de creación descendente
        todasReservas.sort(Comparator.comparing(Reserva::getFechaCreacion).reversed());
        
        // Limitar la cantidad de resultados
        return todasReservas.stream().limit(limite).collect(Collectors.toList());
    }
    
    /**
     * Obtiene los servicios más populares
     * @param limite Número máximo de servicios a retornar
     * @return Mapa con servicios y su frecuencia
     */
    public Map<Servicio, Long> obtenerServiciosPopulares(int limite) {
        List<ServicioReserva> todasRelaciones = servicioReservaRepository.findAll();
        
        // Contar frecuencia de cada servicio
        Map<Servicio, Long> frecuenciaServicios = todasRelaciones.stream()
                .map(ServicioReserva::getServicio)
                .collect(Collectors.groupingBy(s -> s, Collectors.counting()));
        
        // Ordenar por frecuencia descendente
        Map<Servicio, Long> resultado = new LinkedHashMap<>();
        frecuenciaServicios.entrySet().stream()
                .sorted(Map.Entry.<Servicio, Long>comparingByValue().reversed())
                .limit(limite)
                .forEachOrdered(e -> resultado.put(e.getKey(), e.getValue()));
        
        return resultado;
    }
    
    /**
     * Calcula la distribución de estados de reservas
     * @return Mapa con estados y su frecuencia
     */
    public Map<Reserva.EstadoReserva, Long> obtenerDistribucionEstados() {
        List<Reserva> todasReservas = reservaRepository.findAll();
        
        return todasReservas.stream()
                .collect(Collectors.groupingBy(Reserva::getEstado, Collectors.counting()));
    }
    
    /**
     * Calcula las estadísticas de reservas por día de la semana
     * @param periodoSemanas Número de semanas a considerar
     * @return Mapa con días de la semana y cantidad de reservas
     */
    public Map<String, Long> obtenerReservasPorDiaSemana(int periodoSemanas) {
        LocalDateTime fechaFin = LocalDateTime.now();
        LocalDateTime fechaInicio = fechaFin.minusWeeks(periodoSemanas);
        
        List<Reserva> reservasEnPeriodo = reservaRepository.findByHoraInicioBetween(fechaInicio, fechaFin);
        
        // Nombres de los días de la semana en español
        String[] diasSemana = {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"};
        
        // Inicializar mapa con todos los días
        Map<String, Long> reservasPorDia = new LinkedHashMap<>();
        for (String dia : diasSemana) {
            reservasPorDia.put(dia, 0L);
        }
        
        // Contar reservas por día
        for (Reserva reserva : reservasEnPeriodo) {
            int diaSemana = reserva.getHoraInicio().getDayOfWeek().getValue() - 1; // 0-6 (Lunes-Domingo)
            String dia = diasSemana[diaSemana];
            reservasPorDia.put(dia, reservasPorDia.get(dia) + 1);
        }
        
        return reservasPorDia;
    }
    
    /**
     * Obtiene los clientes más frecuentes
     * @param limite Número máximo de clientes a retornar
     * @return Mapa con usuarios y cantidad de reservas
     */
    public Map<Usuario, Long> obtenerClientesFrecuentes(int limite) {
        List<Reserva> todasReservas = reservaRepository.findAll();
        
        // Contar frecuencia de cada usuario
        Map<Usuario, Long> frecuenciaUsuarios = todasReservas.stream()
                .map(Reserva::getUsuario)
                .collect(Collectors.groupingBy(u -> u, Collectors.counting()));
        
        // Ordenar por frecuencia descendente
        Map<Usuario, Long> resultado = new LinkedHashMap<>();
        frecuenciaUsuarios.entrySet().stream()
                .sorted(Map.Entry.<Usuario, Long>comparingByValue().reversed())
                .limit(limite)
                .forEachOrdered(e -> resultado.put(e.getKey(), e.getValue()));
        
        return resultado;
    }
}