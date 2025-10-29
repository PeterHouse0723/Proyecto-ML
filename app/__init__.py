from flask import Flask
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la instancia de Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

from app import routes