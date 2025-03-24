-- Paso 1: Insertar usuarios de prueba
INSERT INTO usuarios (nombre, apellido, correo, contrasena) VALUES
('Ana', 'García', 'ana@example.com', 'password123'),
('Carlos', 'Pérez', 'carlos@example.com', 'password123'),
('María', 'López', 'maria@example.com', 'password123');

-- Verificar que los usuarios se crearon correctamente
SELECT id, nombre, apellido, correo FROM usuarios; 