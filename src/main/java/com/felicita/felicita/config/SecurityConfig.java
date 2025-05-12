package com.felicita.felicita.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import com.felicita.felicita.security.JwtAuthorizationFilter;
import com.felicita.felicita.security.JwtTokenProvider;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;

    public SecurityConfig(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // Configurar CORS - usar método moderno
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            // Deshabilitar CSRF para APIs REST
            .csrf(csrf -> csrf.disable())
            // Configurar manejo de sesiones
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            // Configurar reglas de autorización
            .authorizeHttpRequests(authorize -> authorize
                // Recursos estáticos - siempre públicos
                .requestMatchers("/css/**", "/js/**", "/images/**", "/webjars/**", "/favicon.ico").permitAll()
                
                // Rutas públicas principales
                .requestMatchers("/", "/home", "/index", "/error", "/error/**").permitAll()
                
                // Páginas informativas - siempre públicas
                .requestMatchers("/servicios", "/contacto", "/nosotros", "/terminos", "/privacidad", "/faq").permitAll()
                
                // API de servicios - clave para mostrar servicios sin login
                .requestMatchers("/api/servicios/**").permitAll()
                
                // Autenticación
                .requestMatchers("/login", "/registro").permitAll()
                .requestMatchers("/api/auth/**").permitAll()
                
                // Rutas protegidas por rol o autenticación
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .requestMatchers("/reservas/**").authenticated()
                .requestMatchers("/api/reservas/**").authenticated()
                .requestMatchers("/perfil/**").authenticated()
                
                // Todo lo demás requiere autenticación
                .anyRequest().authenticated()
            )
            // Añadir filtro JWT
            .addFilterBefore(new JwtAuthorizationFilter(jwtTokenProvider), UsernamePasswordAuthenticationFilter.class)
            
            // Configurar formulario de login
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/", true)
                .permitAll()
            )
            
            // Configurar logout
            .logout(logout -> logout
                .logoutSuccessUrl("/login?logout")
                .permitAll()
            );
        
        return http.build();
    }

    @Bean
    CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type"));
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}