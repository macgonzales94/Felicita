package com.felicita.felicita.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Clase que representa un negocio de belleza (salón o barbería) en el sistema.
 */
@Entity
@Table(name = "negocios")
public class Negocio {
    
    /**
     * Identificador único del negocio
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * Usuario propietario del negocio (con rol PROADMIN)
     */
    @OneToOne
    @JoinColumn(name = "id_usuario", nullable = false)
    private Usuario usuario;
    
    /**
     * Nombre comercial del negocio
     */
    @NotBlank
    @Size(max = 100)
    @Column(name = "nombre_comercial")
    private String nombreComercial;
    
    /**
     * Descripción del negocio
     */
    @Column(name = "descripcion", columnDefinition = "TEXT")
    private String descripcion;
    
    /**
     * Dirección física del negocio
     */
    @NotBlank
    @Size(max = 200)
    @Column(name = "direccion")
    private String direccion;
    
    /**
     * Teléfono de contacto del negocio
     */
    @Size(max = 20)
    @Column(name = "telefono")
    private String telefono;
    
    /**
     * Correo electrónico de contacto del negocio
     */
    @Size(max = 50)
    @Column(name = "correo_contacto")
    private String correoContacto;
    
    /**
     * URL del logo del negocio
     */
    @Column(name = "logo")
    private String logo;
    
    /**
     * Horario de operación en formato JSON
     */
    @Column(name = "horario_operacion", columnDefinition = "TEXT")
    private String horarioOperacion;
    
    /**
     * Indica si el negocio está verificado por los administradores
     */
    @Column(name = "verificado")
    private boolean verificado = false;
    
    /**
     * Fecha de registro del negocio
     */
    @Column(name = "fecha_registro")
    private LocalDateTime fechaRegistro;
    
    /**
     * Estado del negocio (ACTIVO, SUSPENDIDO, INACTIVO)
     */
    @Column(name = "estado")
    private String estado = "ACTIVO";
    
    /**
     * Tipo de negocio (SALON, BARBERIA, AMBOS)
     */
    @Column(name = "tipo")
    private String tipo;
    
    /**
     * Coordenadas de ubicación - Latitud
     */
    @Column(name = "latitud")
    private Double latitud;
    
    /**
     * Coordenadas de ubicación - Longitud
     */
    @Column(name = "longitud")
    private Double longitud;
    
    /**
     * Sitio web del negocio
     */
    @Column(name = "sitio_web")
    private String sitioWeb;
    
    /**
     * Redes sociales en formato JSON
     */
    @Column(name = "redes_sociales", columnDefinition = "TEXT")
    private String redesSociales;
    
    /**
     * Lista de empleados del negocio
     */
    @OneToMany(mappedBy = "negocio", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Empleado> empleados = new ArrayList<>();
    
    /**
     * Lista de servicios ofrecidos por el negocio
     */
    @OneToMany(mappedBy = "negocio", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Servicio> servicios = new ArrayList<>();
    
    /**
     * Constructor por defecto
     */
    public Negocio() {
        this.fechaRegistro = LocalDateTime.now();
    }
    
    /**
     * Constructor con parámetros principales
     */
    public Negocio(Usuario usuario, String nombreComercial, String direccion) {
        this.usuario = usuario;
        this.nombreComercial = nombreComercial;
        this.direccion = direccion;
        this.fechaRegistro = LocalDateTime.now();
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public void setUsuario(Usuario usuario) {
        this.usuario = usuario;
    }

    public String getNombreComercial() {
        return nombreComercial;
    }

    public void setNombreComercial(String nombreComercial) {
        this.nombreComercial = nombreComercial;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getDireccion() {
        return direccion;
    }

    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public String getCorreoContacto() {
        return correoContacto;
    }

    public void setCorreoContacto(String correoContacto) {
        this.correoContacto = correoContacto;
    }

    public String getLogo() {
        return logo;
    }

    public void setLogo(String logo) {
        this.logo = logo;
    }

    public String getHorarioOperacion() {
        return horarioOperacion;
    }

    public void setHorarioOperacion(String horarioOperacion) {
        this.horarioOperacion = horarioOperacion;
    }

    public boolean isVerificado() {
        return verificado;
    }

    public void setVerificado(boolean verificado) {
        this.verificado = verificado;
    }

    public LocalDateTime getFechaRegistro() {
        return fechaRegistro;
    }

    public void setFechaRegistro(LocalDateTime fechaRegistro) {
        this.fechaRegistro = fechaRegistro;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public String getTipo() {
        return tipo;
    }

    public void setTipo(String tipo) {
        this.tipo = tipo;
    }

    public Double getLatitud() {
        return latitud;
    }

    public void setLatitud(Double latitud) {
        this.latitud = latitud;
    }

    public Double getLongitud() {
        return longitud;
    }

    public void setLongitud(Double longitud) {
        this.longitud = longitud;
    }

    public String getSitioWeb() {
        return sitioWeb;
    }

    public void setSitioWeb(String sitioWeb) {
        this.sitioWeb = sitioWeb;
    }

    public String getRedesSociales() {
        return redesSociales;
    }

    public void setRedesSociales(String redesSociales) {
        this.redesSociales = redesSociales;
    }

    public List<Empleado> getEmpleados() {
        return empleados;
    }

    public void setEmpleados(List<Empleado> empleados) {
        this.empleados = empleados;
    }

    public List<Servicio> getServicios() {
        return servicios;
    }

    public void setServicios(List<Servicio> servicios) {
        this.servicios = servicios;
    }
}