from flask import Flask

# Crear la instancia de Flask
app = Flask(__name__)

# Importar las rutas
app.secret_key = "Pp0723*"

from app import routes