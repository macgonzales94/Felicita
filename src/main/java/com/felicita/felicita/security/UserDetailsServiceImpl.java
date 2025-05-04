package com.felicita.felicita.security;

import com.felicita.felicita.model.Usuario;
import com.felicita.felicita.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

/**
 * Servicio que carga los detalles de usuario desde la base de datos.
 * Implementa UserDetailsService de Spring Security.
 */
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Override
    public UserDetails loadUserByUsername(String nombreUsuario) throws UsernameNotFoundException {
        Usuario usuario = usuarioRepository.findByNombreUsuario(nombreUsuario)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado: " + nombreUsuario));

        List<GrantedAuthority> autoridades = Collections.singletonList(
                new SimpleGrantedAuthority("ROLE_" + usuario.getRol()));

        return new User(
                usuario.getNombreUsuario(),
                usuario.getContraseña(),
                true,         // enabled
                true,         // accountNonExpired
                true,         // credentialsNonExpired
                true,         // accountNonLocked
                autoridades);
    }
}