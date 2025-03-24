-- Paso 3: Insertar interacciones (likes, favoritos, comentarios)
-- Primero verificamos que existan las publicaciones
SELECT id, titulo FROM publicaciones;

-- Insertar likes
INSERT INTO likes (usuario_id, publicacion_id) VALUES
-- Ana (id:1) le gusta ropa formal/elegante
(1, 2), -- Like al blazer formal
(1, 4), -- Like al vestido de fiesta

-- Carlos (id:2) le gusta ropa casual/vintage
(2, 1), -- Like al vestido floral
(2, 3), -- Like a los jeans vintage

-- María (id:3) le gusta ropa deportiva y casual
(3, 5), -- Like al conjunto deportivo
(3, 1); -- Like al vestido floral

-- Verificar los likes
SELECT l.*, p.titulo 
FROM likes l 
JOIN publicaciones p ON l.publicacion_id = p.id;

-- Insertar favoritos
INSERT INTO favoritos (usuario_id, publicacion_id) VALUES
(1, 4), -- Ana: Favorito al vestido de fiesta
(2, 3), -- Carlos: Favorito a los jeans vintage
(3, 5); -- María: Favorito al conjunto deportivo

-- Verificar los favoritos
SELECT f.*, p.titulo 
FROM favoritos f 
JOIN publicaciones p ON f.publicacion_id = p.id;

-- Insertar comentarios
INSERT INTO comentarios (usuario_id, publicacion_id, comentario) VALUES
(1, 2, '¡Me encanta este blazer! Es perfecto para el trabajo y muy elegante.'),
(1, 4, 'El vestido es hermoso y el precio del alquiler es muy razonable.'),
(2, 1, 'El vestido es bonito pero el precio es un poco alto.'),
(2, 3, '¡Los jeans son geniales! Me encantan los detalles vintage.'),
(3, 5, 'La calidad del conjunto deportivo es excelente, muy cómodo para ejercitar.'),
(3, 1, 'No me convence mucho el estampado floral.');

-- Verificar los comentarios
SELECT c.*, p.titulo 
FROM comentarios c 
JOIN publicaciones p ON c.publicacion_id = p.id; 