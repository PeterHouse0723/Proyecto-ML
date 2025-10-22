from flask import render_template, request, redirect, url_for
from app import app

# Usuarios de prueba
usuarios = {
    "Peter": "1234",
    "Maria": "abcd",
    "Sebastian": "caec2025"
}

@app.route('/')
def home():
    # Redirige automáticamente a inicio (página pública)
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    # Página de inicio pública (sin necesidad de login)
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validación del usuario
        if username in usuarios and usuarios[username] == password:
            # Si todo está bien, lleva al usuario al index
            return redirect(url_for('index'))
        else:
            # Si las credenciales son incorrectas, muestra el error
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    # Si es GET, solo muestra el formulario
    return render_template('login.html')

@app.route('/index')
def index():
    # Página protegida (requiere login)
    return render_template('index.html')

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route('/newuser')
def newuser():
    return render_template('newuser.html')
