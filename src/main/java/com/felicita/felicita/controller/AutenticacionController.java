package com.felicita.felicita.controller;

import com.felicita.felicita.dto.LoginRequest;
import com.felicita.felicita.dto.RegistroRequest;
import com.felicita.felicita.dto.RegistroNegocioRequest;
import com.felicita.felicita.dto.JwtResponse;
import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.service.AutenticacionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

/**
 * Controlador que maneja las operaciones de autenticación.
 * Expone endpoints para iniciar sesión y registrar usuarios.
 */
@RestController
@RequestMapping("/api/auth")
public class AutenticacionController {

    @Autowired
    private AutenticacionService autenticacionService;

    /**
     * Endpoint para iniciar sesión
     * @param loginRequest Datos de inicio de sesión
     * @return Token JWT si la autenticación es exitosa
     */
    @PostMapping("/login")
    public ResponseEntity<JwtResponse> iniciarSesion(@Valid @RequestBody LoginRequest loginRequest) {
        JwtResponse jwtResponse = autenticacionService.autenticarUsuario(loginRequest);
        return ResponseEntity.ok(jwtResponse);
    }

    /**
     * Endpoint para registrar un nuevo usuario cliente
     * @param registroRequest Datos de registro
     * @return Mensaje indicando el resultado del registro
     */
    @PostMapping("/registro")
    public ResponseEntity<MensajeResponse> registrarUsuario(@Valid @RequestBody RegistroRequest registroRequest) {
        MensajeResponse mensaje = autenticacionService.registrarUsuario(registroRequest);
        if (mensaje.isExito()) {
            return ResponseEntity.ok(mensaje);
        } else {
            return ResponseEntity.badRequest().body(mensaje);
        }
    }
    
    /**
     * Endpoint para registrar un nuevo negocio
     * @param registroRequest Datos de registro del negocio
     * @return Mensaje indicando el resultado del registro
     */
    @PostMapping("/registro-negocio")
    public ResponseEntity<MensajeResponse> registrarNegocio(@Valid @RequestBody RegistroNegocioRequest registroRequest) {
        MensajeResponse mensaje = autenticacionService.registrarNegocio(registroRequest);
        if (mensaje.isExito()) {
            return ResponseEntity.ok(mensaje);
        } else {
            return ResponseEntity.badRequest().body(mensaje);
        }
    }
}