-- Insertar Empleados
INSERT INTO empleados (nombre, cargo, foto, activo)
VALUES 
('Ana Rojas', 'Estilista Senior', '/images/stylist-1.jpg', 1),
('Carmen Silva', 'Especialista en Color', '/images/stylist-2.jpg', 1),
('Luis Mendoza', 'Barbero Profesional', '/images/barber-1.jpg', 1),
('Roberto Torres', 'Esteticista', '/images/stylist-3.jpg', 1),
('Marta Flores', 'Manicurista', '/images/stylist-4.jpg', 1),
('Javier Morales', 'Masajista', '/images/stylist-5.jpg', 1),
('Valeria Díaz', 'Directivo', '/images/director-1.jpg', 1),
('Daniel Paredes', 'Directivo', '/images/director-2.jpg', 1);

-- Insertar Disponibilidad de Empleados (para una semana)
-- Empleado 1: Ana Rojas
INSERT INTO disponibilidades (id_empleado, dia, hora_inicio, hora_fin, disponible)
VALUES 
(1, CURDATE(), '09:00:00', '18:00:00', 1),
(1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00', '18:00:00', 1),
(1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '09:00:00', '18:00:00', 1),
(1, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '09:00:00', '18:00:00', 1),
(1, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '09:00:00', '18:00:00', 1),
(1, DATE_ADD(CURDATE(), INTERVAL 5 DAY), '10:00:00', '15:00:00', 1);

-- Empleado 2: Carmen Silva
INSERT INTO disponibilidades (id_empleado, dia, hora_inicio, hora_fin, disponible)
VALUES 
(2, CURDATE(), '10:00:00', '19:00:00', 1),
(2, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00:00', '19:00:00', 1),
(2, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '10:00:00', '19:00:00', 1),
(2, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '10:00:00', '19:00:00', 1),
(2, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '10:00:00', '19:00:00', 1);

-- Empleado 3: Luis Mendoza
INSERT INTO disponibilidades (id_empleado, dia, hora_inicio, hora_fin, disponible)
VALUES 
(3, CURDATE(), '08:00:00', '17:00:00', 1),
(3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '17:00:00', 1),
(3, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00:00', '17:00:00', 1),
(3, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '08:00:00', '17:00:00', 1),
(3, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '08:00:00', '17:00:00', 1),
(3, DATE_ADD(CURDATE(), INTERVAL 6 DAY), '09:00:00', '14:00:00', 1);

-- Insertar Testimonios
INSERT INTO testimonios (nombre_cliente, id_usuario, mensaje, valoracion, fecha, activo, id_servicio, cargo_cliente, imagen_cliente)
VALUES 
('María García', 2, '¡FELICITA ha revolucionado la forma en que reservo mis citas de belleza! La plataforma es súper fácil de usar y me permite encontrar los mejores profesionales en cualquier momento.', 5, NOW(), 1, 1, 'Cliente frecuente', '/images/avatar-1.jpg'),
('Juan Pérez', 3, 'Excelente servicio. Los barberos son verdaderos profesionales, y la facilidad para reservar y cancelar citas es increíble.', 5, NOW(), 1, 16, 'Empresario', '/images/avatar-2.jpg'),
('Laura Rodríguez', 4, 'Nunca había tenido una experiencia tan placentera reservando servicios de belleza. Definitivamente, FELICITA ha cambiado mi rutina de belleza para siempre.', 4, NOW(), 1, 6, 'Diseñadora', '/images/avatar-3.jpg'),
('Carlos Sánchez', 5, 'La calidad de los servicios y la facilidad para reservar me han convertido en cliente habitual. ¡100% recomendado!', 5, NOW(), 1, 18, 'Ingeniero', '/images/avatar-4.jpg'),
('Ana López', NULL, 'Me encanta poder ver las reseñas de otros clientes antes de elegir mi estilista. Siempre encuentro lo que busco con FELICITA.', 4, NOW(), 1, 2, 'Abogada', '/images/avatar-5.jpg'),
('Pedro Martínez', NULL, 'Reservar mi corte de cabello mensual nunca fue tan fácil. La aplicación es intuitiva y los recordatorios son muy útiles.', 5, NOW(), 1, 3, 'Profesor', '/images/avatar-6.jpg');

-- Insertar algunas Reservas
-- Reserva 1: María reserva un Corte de Cabello con Ana
INSERT INTO reservas (id_usuario, id_empleado, hora_inicio, hora_fin, estado, notas, fecha_creacion)
VALUES 
(2, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL '10:00' HOUR_MINUTE, 
    DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL '10:30' HOUR_MINUTE, 
    'CONFIRMADA', 'Prefiero un corte moderno', NOW());

-- Asociar servicio a reserva
INSERT INTO servicios_reservas (id_reserva, id_servicio)
VALUES (1, 1);

-- Reserva 2: Juan reserva un Corte de Barba con Luis
INSERT INTO reservas (id_usuario, id_empleado, hora_inicio, hora_fin, estado, notas, fecha_creacion)
VALUES 
(3, 3, DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL '11:00' HOUR_MINUTE, 
    DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL '11:25' HOUR_MINUTE, 
    'CONFIRMADA', 'Perfilado y recorte', NOW());

-- Asociar servicio a reserva
INSERT INTO servicios_reservas (id_reserva, id_servicio)
VALUES (2, 16);

-- Reserva 3: Laura reserva una Manicura con Marta
INSERT INTO reservas (id_usuario, id_empleado, hora_inicio, hora_fin, estado, notas, fecha_creacion)
VALUES 
(4, 5, DATE_ADD(CURDATE(), INTERVAL 3 DAY) + INTERVAL '15:00' HOUR_MINUTE, 
    DATE_ADD(CURDATE(), INTERVAL 3 DAY) + INTERVAL '15:45' HOUR_MINUTE, 
    'PENDIENTE', 'Me gustaría un diseño floral', NOW());

-- Asociar servicio a reserva
INSERT INTO servicios_reservas (id_reserva, id_servicio)
VALUES (3, 6);

-- Reserva 4: María reserva un Masaje Relajante con Javier
INSERT INTO reservas (id_usuario, id_empleado, hora_inicio, hora_fin, estado, notas, fecha_creacion)
VALUES 
(2, 6, DATE_ADD(CURDATE(), INTERVAL 4 DAY) + INTERVAL '16:00' HOUR_MINUTE, 
    DATE_ADD(CURDATE(), INTERVAL 4 DAY) + INTERVAL '17:00' HOUR_MINUTE, 
    'PENDIENTE', 'Presión media, por favor', NOW());

-- Asociar servicio a reserva
INSERT INTO servicios_reservas (id_reserva, id_servicio)
VALUES (4, 21);-- Script para cargar datos de prueba en la base de datos de FELICITA

-- Eliminar datos existentes para evitar conflictos (opcional, según necesidad)
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE servicios_reservas;
-- TRUNCATE TABLE reservas;
-- TRUNCATE TABLE servicios;
-- TRUNCATE TABLE categorias;
-- TRUNCATE TABLE empleados;
-- TRUNCATE TABLE usuarios;
-- TRUNCATE TABLE testimonios;
-- TRUNCATE TABLE disponibilidades;
-- SET FOREIGN_KEY_CHECKS = 1;

-- Insertar Categorías
INSERT INTO categorias (nombre, descripcion, icono, orden, activo)
VALUES 
('Cabello', 'Servicios para el cuidado y estilizado del cabello', 'fa-cut', 1, 1),
('Uñas', 'Servicios de manicura y pedicura', 'fa-hand-sparkles', 2, 1),
('Facial', 'Tratamientos faciales y limpieza', 'fa-spa', 3, 1),
('Barbería', 'Servicios especializados para caballeros', 'fa-razor', 4, 1),
('Spa', 'Servicios de relajación y bienestar', 'fa-hot-tub', 5, 1);

-- Insertar Servicios
INSERT INTO servicios (nombre, descripcion, precio, duracion, imagen, activo, id_categoria, destacado, calificacion, num_calificaciones)
VALUES 
-- Servicios de Cabello
('Corte de Cabello', 'Cortes modernos y personalizados para destacar tu estilo único.', 35.00, 30, '/images/service-hair-cut.jpg', 1, 1, 1, 4.8, 125),
('Tinte', 'Coloración profesional con productos de alta calidad para un resultado duradero.', 60.00, 90, '/images/service-hair-color.jpg', 1, 1, 1, 4.6, 98),
('Peinado', 'Peinados para eventos especiales realizados por estilistas expertos.', 45.00, 45, '/images/service-hair-styling.jpg', 1, 1, 0, 4.7, 85),
('Tratamiento Capilar', 'Hidratación profunda y reparación para cabellos dañados.', 50.00, 60, '/images/service-hair-treatment.jpg', 1, 1, 0, 4.9, 65),
('Extensiones', 'Extensiones de cabello natural para dar volumen y longitud.', 150.00, 120, '/images/service-hair-extensions.jpg', 1, 1, 0, 4.7, 42),

-- Servicios de Uñas
('Manicure', 'Cuidado profesional para tus uñas con los mejores productos.', 40.00, 45, '/images/service-manicure.jpg', 1, 2, 1, 4.5, 110),
('Pedicure', 'Tratamiento completo para pies: exfoliación, hidratación y esmaltado.', 50.00, 60, '/images/service-pedicure.jpg', 1, 2, 0, 4.6, 87),
('Uñas Acrílicas', 'Extensiones de uñas duraderas con diseños personalizados.', 70.00, 90, '/images/service-acrylic-nails.jpg', 1, 2, 0, 4.4, 62),
('Esmaltado Semipermanente', 'Esmalte de larga duración con secado instantáneo.', 45.00, 45, '/images/service-gel-polish.jpg', 1, 2, 1, 4.7, 93),
('Nail Art', 'Diseños artísticos y decoraciones para tus uñas.', 30.00, 30, '/images/service-nail-art.jpg', 1, 2, 0, 4.8, 75),

-- Servicios Faciales
('Limpieza Facial Profunda', 'Tratamiento profundo para eliminar impurezas y toxinas.', 60.00, 60, '/images/service-facial.jpg', 1, 3, 1, 4.9, 88),
('Microdermoabrasión', 'Exfoliación profesional para renovar la piel.', 80.00, 45, '/images/service-microdermabrasion.jpg', 1, 3, 0, 4.7, 56),
('Hidratación Facial', 'Tratamiento intensivo para pieles secas o deshidratadas.', 50.00, 45, '/images/service-facial-hydration.jpg', 1, 3, 0, 4.8, 67),
('Tratamiento Anti-Edad', 'Reduce líneas de expresión y signos de envejecimiento.', 90.00, 60, '/images/service-anti-aging.jpg', 1, 3, 0, 4.9, 48),
('Mascarilla de Colágeno', 'Revitaliza y rejuvenece la piel con proteínas naturales.', 40.00, 30, '/images/service-collagen-mask.jpg', 1, 3, 0, 4.6, 52),

-- Servicios de Barbería
('Corte de Barba', 'Perfilado y tratamiento de barba con productos premium.', 25.00, 25, '/images/service-beard.jpg', 1, 4, 1, 4.8, 105),
('Afeitado Clásico', 'Afeitado tradicional con navaja y toallas calientes.', 35.00, 30, '/images/service-shave.jpg', 1, 4, 0, 4.7, 82),
('Corte Masculino', 'Estilizado y corte de cabello para caballeros.', 30.00, 30, '/images/service-mens-haircut.jpg', 1, 4, 1, 4.9, 120),
('Coloración de Barba', 'Tinte para barba que oculta canas y rejuvenece tu aspecto.', 40.00, 45, '/images/service-beard-color.jpg', 1, 4, 0, 4.5, 38),
('Tratamiento Capilar Masculino', 'Combate la caída del cabello y fortalece el cuero cabelludo.', 45.00, 40, '/images/service-scalp-treatment.jpg', 1, 4, 0, 4.6, 45),

-- Servicios de Spa
('Masaje Relajante', 'Técnicas de masaje para aliviar tensiones y estrés.', 70.00, 60, '/images/service-massage.jpg', 1, 5, 1, 4.9, 95),
('Tratamiento Corporal', 'Exfoliación e hidratación para todo el cuerpo.', 80.00, 75, '/images/service-body-treatment.jpg', 1, 5, 0, 4.8, 62),
('Reflexología', 'Masaje especializado en pies para estimular puntos energéticos.', 60.00, 45, '/images/service-reflexology.jpg', 1, 5, 0, 4.7, 48),
('Aromaterapia', 'Masaje con aceites esenciales para equilibrar cuerpo y mente.', 75.00, 60, '/images/service-aromatherapy.jpg', 1, 5, 0, 4.9, 56),
('Piedras Calientes', 'Terapia con piedras calientes para relajación profunda.', 90.00, 75, '/images/service-hot-stones.jpg', 1, 5, 0, 4.8, 42);

-- Insertar Usuarios (contraseña: password123)
INSERT INTO usuarios (nombre_usuario, correo, contraseña, nombre_completo, telefono, rol, fecha_creacion)
VALUES 
('admin', 'admin@felicita.pe', '$2a$10$yXAHJgYUQcZJ.U5ASKFzcO2C0VTxM9QrnOK0RsXxiH8EzHHQTNrCS', 'Administrador Sistema', '+51987654321', 'ADMIN', NOW()),
('maria', 'maria@example.com', '$2a$10$yXAHJgYUQcZJ.U5ASKFzcO2C0VTxM9QrnOK0RsXxiH8EzHHQTNrCS', 'María García', '+51987654322', 'CLIENTE', NOW()),
('juan', 'juan@example.com', '$2a$10$yXAHJgYUQcZJ.U5ASKFzcO2C0VTxM9QrnOK0RsXxiH8EzHHQTNrCS', 'Juan Pérez', '+51987654323', 'CLIENTE', NOW()),
('laura', 'laura@example.com', '$2a$10$yXAHJgYUQcZJ.U5ASKFzcO2C0VTxM9QrnOK0RsXxiH8EzHHQTNrCS', 'Laura Rodríguez', '+51987654324', 'CLIENTE', NOW()),
('carlos', 'carlos@example.com', '$2a$10$yXAHJgYUQcZJ.U5ASKFzcO2C0VTxM9QrnOK0RsXxiH8EzHHQTNrCS', 'Carlos Sánchez', '+51987654325', 'CLIENTE', NOW());