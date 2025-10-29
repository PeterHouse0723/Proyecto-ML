import mysql.connector
from mysql.connector import Error
import os

class Database:
    """Clase para gestionar la conexión a la base de datos MySQL"""

    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'proyecto_ml')
        self.connection = None

    def connect(self):
        """Establece la conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None

    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """Ejecuta una consulta INSERT, UPDATE o DELETE"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error al ejecutar query: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def fetch_query(self, query, params=None):
        """Ejecuta una consulta SELECT y retorna los resultados"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error al ejecutar query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

# Instancia global de la base de datos
db = Database()
