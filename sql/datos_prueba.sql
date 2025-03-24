-- Insertar usuarios de prueba
INSERT INTO usuarios (nombre, apellido, correo, contrasena) VALUES
('Ana', 'García', 'ana@example.com', 'password123'),
('Carlos', 'Pérez', 'carlos@example.com', 'password123'),
('María', 'López', 'maria@example.com', 'password123');

-- Insertar publicaciones de prueba con diferentes características
INSERT INTO publicaciones (usuario_id, titulo, descripcion, imagen_url, precio, tipo, publico, talla, estilo, colores) VALUES
(1, 'Vestido floral verano', 'Hermoso vestido floral perfecto para el verano', 'https://ejemplo.com/vestido1.jpg', 45.99, 'venta', 'mujer', 'M', ARRAY['casual', 'elegante'], ARRAY['azul', 'blanco']),
(1, 'Blazer formal', 'Blazer negro formal para ocasiones especiales', 'https://ejemplo.com/blazer1.jpg', 89.99, 'venta', 'mujer', 'S', ARRAY['formal', 'elegante'], ARRAY['negro']),
(2, 'Jeans vintage', 'Jeans de estilo vintage', 'https://ejemplo.com/jeans1.jpg', 15.00, 'alquiler', 'mujer', 'M', ARRAY['casual', 'vintage'], ARRAY['azul']),
(2, 'Vestido de fiesta', 'Vestido elegante para eventos', 'https://ejemplo.com/vestido2.jpg', 25.00, 'alquiler', 'mujer', 'L', ARRAY['elegante', 'formal'], ARRAY['rojo', 'negro']),
(3, 'Conjunto deportivo', 'Conjunto para hacer ejercicio', 'https://ejemplo.com/deportivo1.jpg', 35.99, 'venta', 'mujer', 'M', ARRAY['deportivo'], ARRAY['gris', 'rosa']);

-- Insertar likes (usuario 1 le gusta ropa formal/elegante)
INSERT INTO likes (usuario_id, publicacion_id) VALUES
(1, 2), -- Like al blazer formal
(1, 4); -- Like al vestido de fiesta

-- Insertar likes (usuario 2 le gusta ropa casual/vintage)
INSERT INTO likes (usuario_id, publicacion_id) VALUES
(2, 1), -- Like al vestido floral
(2, 3); -- Like a los jeans vintage

-- Insertar likes (usuario 3 le gusta ropa deportiva y casual)
INSERT INTO likes (usuario_id, publicacion_id) VALUES
(3, 5), -- Like al conjunto deportivo
(3, 1); -- Like al vestido floral

-- Insertar favoritos
INSERT INTO favoritos (usuario_id, publicacion_id) VALUES
(1, 4), -- Favorito al vestido de fiesta
(2, 3), -- Favorito a los jeans vintage
(3, 5); -- Favorito al conjunto deportivo

-- Insertar comentarios con diferentes sentimientos
INSERT INTO comentarios (usuario_id, publicacion_id, comentario) VALUES
(1, 2, '¡Me encanta este blazer! Es perfecto para el trabajo y muy elegante.'), -- Comentario positivo
(1, 4, 'El vestido es hermoso y el precio del alquiler es muy razonable.'), -- Comentario positivo
(2, 1, 'El vestido es bonito pero el precio es un poco alto.'), -- Comentario mixto
(2, 3, '¡Los jeans son geniales! Me encantan los detalles vintage.'), -- Comentario positivo
(3, 5, 'La calidad del conjunto deportivo es excelente, muy cómodo para ejercitar.'), -- Comentario positivo
(3, 1, 'No me convence mucho el estampado floral.'); -- Comentario negativo

-- Insertar perfiles de usuario con preferencias
INSERT INTO perfiles_usuario (usuario_id, descripcion, talla, estilos_preferidos, colores_preferidos, ocasiones_uso) VALUES
(1, 'Me gusta la ropa formal y elegante', 'M', 'formal,elegante', 'negro,rojo', 'trabajo,fiesta'),
(2, 'Fan del estilo vintage y casual', 'M', 'vintage,casual', 'azul,blanco', 'casual,diario'),
(3, 'Amante del deporte y la comodidad', 'M', 'deportivo,casual', 'gris,rosa', 'deporte,casual'); 