#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migracion 002: Agregar tabla de resultados para almacenar historial de predicciones
Fecha: 2025-10-31
"""

import sys
import os

# Agregar el directorio raiz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import db

def ejecutar_migracion():
    """Ejecuta la migracion para agregar la tabla resultados"""

    print("Ejecutando migracion 002: Agregar tabla resultados...")

    query = """
    CREATE TABLE IF NOT EXISTS resultados (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        nivel_prediccion VARCHAR(20) NOT NULL,
        puntaje_prediccion DECIMAL(5,2) NOT NULL,
        datos_formulario JSON NOT NULL,
        recomendaciones JSON NOT NULL,
        factores_riesgo JSON NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
        INDEX idx_usuario_fecha (usuario_id, fecha_creacion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    resultado = db.execute_query(query)

    if resultado is not None:
        print("Tabla 'resultados' creada exitosamente!")
        return True
    else:
        print("Error al crear la tabla 'resultados'")
        return False

def revertir_migracion():
    """Revierte la migracion eliminando la tabla resultados"""

    print("Revirtiendo migracion 002...")

    query = "DROP TABLE IF EXISTS resultados"
    resultado = db.execute_query(query)

    if resultado is not None:
        print("Tabla 'resultados' eliminada exitosamente!")
        return True
    else:
        print("Error al eliminar la tabla 'resultados'")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--revert':
        revertir_migracion()
    else:
        ejecutar_migracion()
