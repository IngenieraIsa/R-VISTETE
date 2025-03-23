-- Paso 4: Insertar perfiles de usuario
-- Primero verificamos que existan los usuarios
SELECT id, nombre FROM usuarios;

-- Insertar perfiles de usuario con preferencias
INSERT INTO perfiles_usuario (usuario_id, descripcion, talla, estilos_preferidos, colores_preferidos, ocasiones_uso) VALUES
(1, 'Me gusta la ropa formal y elegante', 'M', 'formal,elegante', 'negro,rojo', 'trabajo,fiesta'),
(2, 'Fan del estilo vintage y casual', 'M', 'vintage,casual', 'azul,blanco', 'casual,diario'),
(3, 'Amante del deporte y la comodidad', 'M', 'deportivo,casual', 'gris,rosa', 'deporte,casual');

-- Verificar los perfiles
SELECT p.*, u.nombre 
FROM perfiles_usuario p 
JOIN usuarios u ON p.usuario_id = u.id; 