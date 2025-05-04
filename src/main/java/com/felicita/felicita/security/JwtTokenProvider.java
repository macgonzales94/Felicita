package com.felicita.felicita.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.stream.Collectors;

/**
 * Componente encargado de generar y validar tokens JWT.
 * Maneja la creación, validación y extracción de información de los tokens.
 */
@Component
public class JwtTokenProvider {

    @Value("${jwt.secreto}")
    private String secreto;

    @Value("${jwt.expiracion}")
    private long expiracion;
    
    /**
     * Clave utilizada para firmar los tokens
     */
    private Key key;
    
    /**
     * Inicializa la clave a partir del secreto configurado
     */
    public void init() {
        this.key = Keys.hmacShaKeyFor(secreto.getBytes());
    }

    /**
     * Genera un token JWT a partir de una autenticación
     * @param authentication La autenticación del usuario
     * @return El token JWT generado
     */
    public String generarToken(Authentication authentication) {
        // El principal es el UserDetails que se devuelve durante la autenticación
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        
        Date ahora = new Date();
        Date fechaExpiracion = new Date(ahora.getTime() + expiracion);
        
        // Obtenemos roles del usuario y los convertimos a una cadena separada por comas
        String autoridades = authentication.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.joining(","));
        
        return Jwts.builder()
                .setSubject(userDetails.getUsername())
                .claim("roles", autoridades)
                .setIssuedAt(ahora)
                .setExpiration(fechaExpiracion)
                .signWith(key, SignatureAlgorithm.HS512)
                .compact();
    }

    /**
     * Extrae el nombre de usuario del token JWT
     * @param token El token JWT
     * @return El nombre de usuario contenido en el token
     */
    public String obtenerNombreUsuarioDelToken(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();

        return claims.getSubject();
    }

    /**
     * Valida si un token JWT es válido
     * @param token El token JWT a validar
     * @return true si el token es válido, false en caso contrario
     */
    public boolean validarToken(String token) {
        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
            return true;
        } catch (SignatureException ex) {
            System.out.println("Firma JWT inválida");
        } catch (MalformedJwtException ex) {
            System.out.println("Token JWT mal formado");
        } catch (ExpiredJwtException ex) {
            System.out.println("Token JWT expirado");
        } catch (UnsupportedJwtException ex) {
            System.out.println("Token JWT no soportado");
        } catch (IllegalArgumentException ex) {
            System.out.println("La cadena claims JWT está vacía");
        }
        return false;
    }

    /**
     * Obtiene la autenticación a partir de un token JWT
     * @param token El token JWT
     * @return La autenticación correspondiente al token
     */
    public Authentication obtenerAutenticacion(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();

        String nombreUsuario = claims.getSubject();
        
        // Extraer roles del claim
        Collection<? extends GrantedAuthority> autoridades =
                Arrays.stream(claims.get("roles").toString().split(","))
                        .map(SimpleGrantedAuthority::new)
                        .collect(Collectors.toList());
        
        // Creamos un objeto principal con los detalles del usuario (sin contraseña)
        org.springframework.security.core.userdetails.User principal = 
                new org.springframework.security.core.userdetails.User(nombreUsuario, "", autoridades);
        
        return new UsernamePasswordAuthenticationToken(principal, token, autoridades);
    }
}