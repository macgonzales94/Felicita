package com.felicita.felicita.service;

import com.felicita.felicita.dto.LoginRequest;
import com.felicita.felicita.dto.RegistroRequest;
import com.felicita.felicita.dto.RegistroNegocioRequest;
import com.felicita.felicita.dto.JwtResponse;
import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.model.Negocio;
import com.felicita.felicita.repository.UsuarioRepository;
import com.felicita.felicita.repository.NegocioRepository;
import com.felicita.felicita.security.JwtTokenProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Servicio que gestiona la autenticación y registro de usuarios.
 */
@Service
public class AutenticacionService {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private UsuarioRepository usuarioRepository;
    
    @Autowired
    private NegocioRepository negocioRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    /**
     * Autentica a un usuario y devuelve un token JWT
     * @param loginRequest Datos de inicio de sesión
     * @return Respuesta con el token JWT
     */
    public JwtResponse autenticarUsuario(LoginRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        loginRequest.getNombreUsuario(),
                        loginRequest.getContraseña()
                )
        );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        String jwt = jwtTokenProvider.generarToken(authentication);
        
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        String rol = userDetails.getAuthorities().stream()
                .findFirst()
                .map(a -> a.getAuthority().replace("ROLE_", ""))
                .orElse("");
        
        return new JwtResponse(jwt, userDetails.getUsername(), rol);
    }

    /**
     * Registra un nuevo usuario en el sistema
     * @param registroRequest Datos de registro
     * @return Mensaje indicando el resultado del registro
     */
    public MensajeResponse registrarUsuario(RegistroRequest registroRequest) {
        // Verificar si el nombre de usuario ya existe
        if (usuarioRepository.existsByNombreUsuario(registroRequest.getNombreUsuario())) {
            return new MensajeResponse("Error: El nombre de usuario ya está en uso", false);
        }

        // Verificar si el correo ya está en uso
        if (usuarioRepository.existsByCorreo(registroRequest.getCorreo())) {
            return new MensajeResponse("Error: El correo electrónico ya está en uso", false);
        }

        // Crear nuevo usuario
        Usuario usuario = new Usuario(
                registroRequest.getNombreUsuario(),
                registroRequest.getCorreo(),
                passwordEncoder.encode(registroRequest.getContraseña()),
                registroRequest.getNombreCompleto(),
                registroRequest.getTelefono()
        );

        // Por defecto, asignar rol CLIENTE
        usuario.setRol("CLIENTE");
        
        usuarioRepository.save(usuario);

        return new MensajeResponse("Usuario registrado exitosamente", true);
    }
    
    /**
     * Registra un nuevo negocio (usuario PROADMIN) en el sistema
     * @param registroRequest Datos de registro
     * @return Mensaje indicando el resultado del registro
     */
    @Transactional
    public MensajeResponse registrarNegocio(RegistroNegocioRequest registroRequest) {
        // Verificar si el nombre de usuario ya existe
        if (usuarioRepository.existsByNombreUsuario(registroRequest.getNombreUsuario())) {
            return new MensajeResponse("Error: El nombre de usuario ya está en uso", false);
        }

        // Verificar si el correo ya está en uso
        if (usuarioRepository.existsByCorreo(registroRequest.getCorreo())) {
            return new MensajeResponse("Error: El correo electrónico ya está en uso", false);
        }

        // Crear nuevo usuario
        Usuario usuario = new Usuario(
                registroRequest.getNombreUsuario(),
                registroRequest.getCorreo(),
                passwordEncoder.encode(registroRequest.getContraseña()),
                registroRequest.getNombreCompleto(),
                registroRequest.getTelefono()
        );

        // Asignar rol PROADMIN
        usuario.setRol("PROADMIN");
        
        // Guardar usuario
        usuario = usuarioRepository.save(usuario);
        
        // Crear negocio asociado
        Negocio negocio = new Negocio();
        negocio.setUsuario(usuario);
        negocio.setNombreComercial(registroRequest.getNombreComercial());
        negocio.setDireccion(registroRequest.getDireccion());
        negocio.setTelefono(registroRequest.getTelefono());
        negocio.setTipo(registroRequest.getTipoNegocio());
        negocio.setVerificado(false);
        negocio.setEstado("ACTIVO");
        
        negocioRepository.save(negocio);

        return new MensajeResponse("Negocio registrado exitosamente. Pendiente de verificación.", true);
    }
}