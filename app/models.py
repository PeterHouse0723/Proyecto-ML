from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    """Modelo para gestionar usuarios en la base de datos"""

    @staticmethod
    def crear_usuario(nombre, apellido, edad, genero, correo, clave):
        """
        Crea un nuevo usuario en la base de datos

        Args:
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            edad (int): Edad del usuario
            genero (str): Género del usuario (M, F, O)
            correo (str): Correo electrónico del usuario
            clave (str): Contraseña en texto plano (se hasheará)

        Returns:
            int: ID del usuario creado, o None si hubo un error
        """
        # Hashear la contraseña
        clave_hasheada = generate_password_hash(clave)

        query = """
            INSERT INTO usuarios (nombre, apellido, edad, genero, correo, clave)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (nombre, apellido, edad, genero, correo, clave_hasheada)

        return db.execute_query(query, params)

    @staticmethod
    def obtener_por_correo(correo):
        """
        Obtiene un usuario por su correo electrónico

        Args:
            correo (str): Correo electrónico del usuario

        Returns:
            dict: Datos del usuario o None si no existe
        """
        query = "SELECT * FROM usuarios WHERE correo = %s"
        params = (correo,)

        resultado = db.fetch_query(query, params)
        return resultado[0] if resultado else None

    @staticmethod
    def verificar_credenciales(correo, clave):
        """
        Verifica las credenciales de un usuario

        Args:
            correo (str): Correo electrónico del usuario
            clave (str): Contraseña en texto plano

        Returns:
            dict: Datos del usuario si las credenciales son correctas, None en caso contrario
        """
        usuario = Usuario.obtener_por_correo(correo)

        if usuario and check_password_hash(usuario['clave'], clave):
            return usuario

        return None

    @staticmethod
    def existe_correo(correo):
        """
        Verifica si un correo ya está registrado

        Args:
            correo (str): Correo electrónico a verificar

        Returns:
            bool: True si el correo existe, False en caso contrario
        """
        usuario = Usuario.obtener_por_correo(correo)
        return usuario is not None

    @staticmethod
    def obtener_todos():
        """
        Obtiene todos los usuarios registrados

        Returns:
            list: Lista de diccionarios con los datos de los usuarios
        """
        query = "SELECT id, nombre, apellido, edad, genero, correo, fecha_registro FROM usuarios"
        return db.fetch_query(query)

    @staticmethod
    def obtener_por_id(usuario_id):
        """
        Obtiene un usuario por su ID

        Args:
            usuario_id (int): ID del usuario

        Returns:
            dict: Datos del usuario o None si no existe
        """
        query = "SELECT id, nombre, apellido, edad, genero, correo, grado_escolaridad, fecha_nacimiento FROM usuarios WHERE id = %s"
        params = (usuario_id,)

        resultado = db.fetch_query(query, params)
        return resultado[0] if resultado else None

    @staticmethod
    def actualizar_usuario(usuario_id, nombre, apellido, edad, genero, correo, grado_escolaridad=None, fecha_nacimiento=None):
        """
        Actualiza los datos de un usuario

        Args:
            usuario_id (int): ID del usuario
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            edad (int): Edad del usuario
            genero (str): Género del usuario
            correo (str): Correo electrónico
            grado_escolaridad (str): Grado de escolaridad
            fecha_nacimiento (str): Fecha de nacimiento (YYYY-MM-DD)

        Returns:
            bool: True si se actualizó correctamente
        """
        query = """
            UPDATE usuarios
            SET nombre = %s, apellido = %s, edad = %s, genero = %s,
                correo = %s, grado_escolaridad = %s, fecha_nacimiento = %s
            WHERE id = %s
        """
        params = (nombre, apellido, edad, genero, correo, grado_escolaridad, fecha_nacimiento, usuario_id)

        resultado = db.execute_query(query, params)
        return resultado is not None
