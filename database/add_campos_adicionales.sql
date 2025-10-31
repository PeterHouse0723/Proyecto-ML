-- Script para añadir campos adicionales a la tabla usuarios
-- Ejecutar este script para actualizar la base de datos existente

USE proyecto_ml;

-- Añadir columnas de grado_escolaridad y fecha_nacimiento si no existen
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS grado_escolaridad VARCHAR(50) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE DEFAULT NULL;

-- Mostrar la estructura actualizada de la tabla
DESCRIBE usuarios;
