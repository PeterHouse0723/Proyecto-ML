import sqlite3
import os
from contextlib import contextmanager

class Database:
    """Clase para gestionar la conexión a la base de datos SQLite"""

    def __init__(self):
        # Obtener ruta de la base de datos desde variable de entorno o usar valor por defecto
        self.db_path = os.getenv('DATABASE_URL', 'instance/proyecto_ml.db')

        # Crear directorio si no existe
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.connection = None
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos creando las tablas si no existen"""
        conn = None
        try:
            # Crear una conexión temporal solo para la inicialización
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # Crear tabla usuarios
            cursor.execute("""
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
                )
            """)

            # Crear índice para correo
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_correo ON usuarios(correo)
            """)

            # Crear tabla resultados
            cursor.execute("""
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
                )
            """)

            # Crear índice compuesto
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_usuario_fecha
                ON resultados(usuario_id, fecha_creacion)
            """)

            conn.commit()
            cursor.close()
            print("Base de datos SQLite inicializada correctamente")
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
        finally:
            # Cerrar la conexión temporal
            if conn:
                conn.close()
            # La conexión de instancia se creará cuando sea necesaria

    def connect(self):
        """Establece la conexión con la base de datos"""
        try:
            # Habilitar foreign keys y row factory para diccionarios
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.row_factory = sqlite3.Row
            return self.connection
        except sqlite3.Error as e:
            print(f"Error al conectar a SQLite: {e}")
            return None

    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()

    @contextmanager
    def get_cursor(self):
        """Context manager para obtener un cursor"""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_query(self, query, params=None):
        """Ejecuta una consulta INSERT, UPDATE o DELETE"""
        try:
            if not self.connection:
                self.connect()

            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                self.connection.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al ejecutar query: {e}")
            if self.connection:
                self.connection.rollback()
            return None

    def fetch_query(self, query, params=None):
        """Ejecuta una consulta SELECT y retorna los resultados"""
        try:
            if not self.connection:
                self.connect()

            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Convertir sqlite3.Row a diccionarios
                rows = cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as e:
            print(f"Error al ejecutar query: {e}")
            return None

# Instancia global de la base de datos
db = Database()
