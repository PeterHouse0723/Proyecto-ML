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

    @staticmethod
    def cambiar_contrasena(usuario_id, clave_actual, clave_nueva):
        """
        Cambia la contraseña de un usuario

        Args:
            usuario_id (int): ID del usuario
            clave_actual (str): Contraseña actual en texto plano
            clave_nueva (str): Nueva contraseña en texto plano

        Returns:
            tuple: (bool, str) - (exito, mensaje)
        """
        # Obtener usuario con contraseña
        query = "SELECT clave FROM usuarios WHERE id = %s"
        resultado = db.fetch_query(query, (usuario_id,))

        if not resultado:
            return False, "Usuario no encontrado"

        usuario = resultado[0]

        # Verificar contraseña actual
        if not check_password_hash(usuario['clave'], clave_actual):
            return False, "Contraseña actual incorrecta"

        # Hash de la nueva contraseña
        clave_nueva_hash = generate_password_hash(clave_nueva)

        # Actualizar contraseña
        query_update = "UPDATE usuarios SET clave = %s WHERE id = %s"
        resultado_update = db.execute_query(query_update, (clave_nueva_hash, usuario_id))

        if resultado_update is not None:
            return True, "Contraseña actualizada exitosamente"
        else:
            return False, "Error al actualizar la contraseña"


class Resultado:
    """Modelo para gestionar resultados de predicciones en la base de datos"""

    @staticmethod
    def guardar_resultado(usuario_id, nivel_prediccion, puntaje_prediccion, datos_formulario, recomendaciones, factores_riesgo):
        """
        Guarda un resultado de predicción en la base de datos

        Args:
            usuario_id (int): ID del usuario
            nivel_prediccion (str): Nivel de riesgo (Bajo, Moderado, Alto)
            puntaje_prediccion (float): Puntaje de la predicción
            datos_formulario (dict): Datos del formulario en formato JSON
            recomendaciones (list): Lista de recomendaciones
            factores_riesgo (list): Lista de factores de riesgo

        Returns:
            int: ID del resultado creado, o None si hubo un error
        """
        import json

        query = """
            INSERT INTO resultados (usuario_id, nivel_prediccion, puntaje_prediccion,
                                   datos_formulario, recomendaciones, factores_riesgo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            usuario_id,
            nivel_prediccion,
            puntaje_prediccion,
            json.dumps(datos_formulario),
            json.dumps(recomendaciones),
            json.dumps(factores_riesgo)
        )

        return db.execute_query(query, params)

    @staticmethod
    def obtener_por_usuario(usuario_id, limite=10):
        """
        Obtiene los resultados de un usuario ordenados por fecha (más recientes primero)

        Args:
            usuario_id (int): ID del usuario
            limite (int): Número máximo de resultados a devolver

        Returns:
            list: Lista de resultados
        """
        import json

        query = """
            SELECT id, nivel_prediccion, puntaje_prediccion,
                   datos_formulario, recomendaciones, factores_riesgo, fecha_creacion
            FROM resultados
            WHERE usuario_id = %s
            ORDER BY fecha_creacion DESC
            LIMIT %s
        """
        params = (usuario_id, limite)

        resultados = db.fetch_query(query, params)

        # Decodificar JSON
        if resultados:
            for resultado in resultados:
                resultado['datos_formulario'] = json.loads(resultado['datos_formulario'])
                resultado['recomendaciones'] = json.loads(resultado['recomendaciones'])
                resultado['factores_riesgo'] = json.loads(resultado['factores_riesgo'])

        return resultados if resultados else []

    @staticmethod
    def obtener_ultimos_7_dias(usuario_id):
        """
        Obtiene los resultados de los últimos 7 días para un usuario

        Args:
            usuario_id (int): ID del usuario

        Returns:
            list: Lista de resultados de la última semana
        """
        import json

        query = """
            SELECT id, nivel_prediccion, puntaje_prediccion,
                   datos_formulario, recomendaciones, factores_riesgo, fecha_creacion
            FROM resultados
            WHERE usuario_id = %s
              AND fecha_creacion >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY fecha_creacion DESC
        """
        params = (usuario_id,)

        resultados = db.fetch_query(query, params)

        # Decodificar JSON
        if resultados:
            for resultado in resultados:
                resultado['datos_formulario'] = json.loads(resultado['datos_formulario'])
                resultado['recomendaciones'] = json.loads(resultado['recomendaciones'])
                resultado['factores_riesgo'] = json.loads(resultado['factores_riesgo'])

        return resultados if resultados else []

    @staticmethod
    def obtener_estadisticas_usuario(usuario_id):
        """
        Obtiene estadísticas resumidas de los resultados de un usuario

        Args:
            usuario_id (int): ID del usuario

        Returns:
            dict: Estadísticas del usuario
        """
        query = """
            SELECT
                COUNT(*) as total_evaluaciones,
                AVG(puntaje_prediccion) as promedio_puntaje,
                MAX(puntaje_prediccion) as puntaje_maximo,
                MIN(puntaje_prediccion) as puntaje_minimo,
                MAX(fecha_creacion) as ultima_evaluacion
            FROM resultados
            WHERE usuario_id = %s
        """
        params = (usuario_id,)

        resultado = db.fetch_query(query, params)
        return resultado[0] if resultado else None
