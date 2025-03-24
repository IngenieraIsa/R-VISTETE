-- Paso 2: Insertar publicaciones de prueba
-- Primero verificamos que existan los usuarios
SELECT id, nombre FROM usuarios;

-- Luego insertamos las publicaciones
INSERT INTO publicaciones (usuario_id, titulo, descripcion, imagen_url, precio, tipo, publico, talla, estilo, colores) VALUES
(1, 'Vestido floral verano', 'Hermoso vestido floral perfecto para el verano', 'https://ejemplo.com/vestido1.jpg', 45.99, 'venta', 'mujer', 'M', ARRAY['casual', 'elegante'], ARRAY['azul', 'blanco']),
(1, 'Blazer formal', 'Blazer negro formal para ocasiones especiales', 'https://ejemplo.com/blazer1.jpg', 89.99, 'venta', 'mujer', 'S', ARRAY['formal', 'elegante'], ARRAY['negro']),
(2, 'Jeans vintage', 'Jeans de estilo vintage', 'https://ejemplo.com/jeans1.jpg', 15.00, 'alquiler', 'mujer', 'M', ARRAY['casual', 'vintage'], ARRAY['azul']),
(2, 'Vestido de fiesta', 'Vestido elegante para eventos', 'https://ejemplo.com/vestido2.jpg', 25.00, 'alquiler', 'mujer', 'L', ARRAY['elegante', 'formal'], ARRAY['rojo', 'negro']),
(3, 'Conjunto deportivo', 'Conjunto para hacer ejercicio', 'https://ejemplo.com/deportivo1.jpg', 35.99, 'venta', 'mujer', 'M', ARRAY['deportivo'], ARRAY['gris', 'rosa']);

-- Verificar que las publicaciones se crearon correctamente
SELECT id, usuario_id, titulo, tipo FROM publicaciones; 