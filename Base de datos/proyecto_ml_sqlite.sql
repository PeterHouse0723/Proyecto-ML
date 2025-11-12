-- Base de datos SQLite: proyecto_ml
-- Script de creación de tablas para SQLite

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    edad INTEGER NOT NULL CHECK (edad > 0),
    genero TEXT NOT NULL CHECK (genero IN ('M', 'F', 'O')),
    correo VARCHAR(255) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    grado_escolaridad VARCHAR(50),
    fecha_nacimiento DATE
);

-- Índice para búsquedas por correo
CREATE INDEX IF NOT EXISTS idx_correo ON usuarios(correo);

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `resultados`
--

CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nivel_prediccion VARCHAR(20) NOT NULL,
    puntaje_prediccion DECIMAL(5,2) NOT NULL,
    datos_formulario TEXT NOT NULL,
    recomendaciones TEXT NOT NULL,
    factores_riesgo TEXT NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índice compuesto para búsquedas por usuario y fecha
CREATE INDEX IF NOT EXISTS idx_usuario_fecha ON resultados(usuario_id, fecha_creacion);
