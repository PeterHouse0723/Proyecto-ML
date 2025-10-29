# Configuración de la Base de Datos MySQL

Este documento explica cómo configurar la base de datos MySQL para el proyecto.

## Requisitos previos

- MySQL Server 5.7 o superior instalado
- Acceso a MySQL con permisos de creación de bases de datos

## Pasos de configuración

### 1. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 2. Crear la base de datos

Opción A - Usando la consola de MySQL:
```bash
mysql -u root -p < database/schema.sql
```

Opción B - Manualmente:
1. Inicia sesión en MySQL:
```bash
mysql -u root -p
```

2. Ejecuta los siguientes comandos:
```sql
CREATE DATABASE IF NOT EXISTS proyecto_ml CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE proyecto_ml;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    edad INT NOT NULL CHECK (edad > 0),
    genero ENUM('M', 'F', 'O') NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correo (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3. Configurar variables de entorno

1. Crea un archivo `.env` en la raíz del proyecto (basado en `.env.example`):
```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tus credenciales de MySQL:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password_de_mysql
DB_NAME=proyecto_ml
SECRET_KEY=genera_una_clave_secreta_aqui
```

**Importante:** Nunca subas el archivo `.env` al repositorio. Asegúrate de que esté en `.gitignore`.

### 4. Verificar la conexión

Puedes crear un script de prueba para verificar la conexión:

```python
from app.database import db

db.connect()
if db.connection and db.connection.is_connected():
    print("✓ Conexión exitosa a MySQL")
    print(f"Base de datos: {db.database}")
else:
    print("✗ Error al conectar a MySQL")
```

## Estructura de la tabla usuarios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | Identificador único (auto-incremental) |
| nombre | VARCHAR(100) | Nombre del usuario |
| apellido | VARCHAR(100) | Apellido del usuario |
| edad | INT | Edad del usuario (debe ser > 0) |
| genero | ENUM('M','F','O') | Género: Masculino, Femenino u Otro |
| correo | VARCHAR(255) | Correo electrónico (único) |
| clave | VARCHAR(255) | Contraseña hasheada |
| fecha_registro | TIMESTAMP | Fecha y hora de registro |

## Funcionalidades implementadas

### Modelo Usuario (`app/models.py`)

- `crear_usuario()`: Registra un nuevo usuario con contraseña hasheada
- `obtener_por_correo()`: Busca un usuario por correo electrónico
- `verificar_credenciales()`: Valida correo y contraseña
- `existe_correo()`: Verifica si un correo ya está registrado
- `obtener_todos()`: Lista todos los usuarios (sin mostrar contraseñas)

### Ruta de registro (`/register`)

El formulario en `/newuser` envía los datos a `/register` que:
1. Valida todos los campos
2. Verifica que las contraseñas coincidan
3. Comprueba que el correo no esté registrado
4. Hashea la contraseña
5. Guarda el usuario en la base de datos
6. Redirige al login con mensaje de éxito

## Seguridad

- Las contraseñas se almacenan hasheadas usando `werkzeug.security`
- Se usa prepared statements para prevenir SQL injection
- El correo electrónico tiene índice y constraint UNIQUE
- Variables de entorno para credenciales sensibles

## Troubleshooting

### Error: "Access denied for user"
Verifica que las credenciales en `.env` sean correctas.

### Error: "Unknown database"
Asegúrate de haber ejecutado el script `schema.sql`.

### Error: "Can't connect to MySQL server"
Verifica que MySQL esté ejecutándose:
```bash
# Windows
net start MySQL

# Linux/Mac
sudo systemctl start mysql
```
