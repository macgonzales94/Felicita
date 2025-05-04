package com.felicita.felicita.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Filtro que intercepta todas las solicitudes y verifica si contienen un token JWT válido.
 * Si el token es válido, establece la autenticación en el contexto de seguridad.
 */
public class JwtAuthorizationFilter extends OncePerRequestFilter {

    private JwtTokenProvider jwtTokenProvider;

    public JwtAuthorizationFilter(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        String token = obtenerJwtDeSolicitud(request);
        
        if (token != null && jwtTokenProvider.validarToken(token)) {
            Authentication auth = jwtTokenProvider.obtenerAutenticacion(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        
        filterChain.doFilter(request, response);
    }

    /**
     * Extrae el token JWT del encabezado de autorización
     * @param request La solicitud HTTP
     * @return El token JWT o null si no existe
     */
    private String obtenerJwtDeSolicitud(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}