from flask import render_template, request, redirect, url_for, flash
from app import app
from app.models import Usuario

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

        # Primero verificar en el diccionario de usuarios de prueba (backwards compatibility)
        if username in usuarios and usuarios[username] == password:
            # Si todo está bien, lleva al usuario al index
            return redirect(url_for('index'))

        # Si no está en usuarios de prueba, verificar en la base de datos
        # Intentar con el username como correo electrónico
        usuario_db = Usuario.verificar_credenciales(username, password)

        if usuario_db:
            # Credenciales válidas desde la base de datos
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

@app.route('/register', methods=['POST'])
def register():
    """Procesa el registro de un nuevo usuario"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        edad = request.form.get('edad', type=int)
        genero = request.form.get('genero', '')
        correo = request.form.get('correo', '').strip().lower()
        clave = request.form.get('clave', '')
        confirmar_clave = request.form.get('confirmar_clave', '')

        # Validaciones
        if not all([nombre, apellido, edad, genero, correo, clave, confirmar_clave]):
            return render_template('newuser.html', error="Todos los campos son obligatorios")

        if clave != confirmar_clave:
            return render_template('newuser.html', error="Las contraseñas no coinciden")

        if len(clave) < 6:
            return render_template('newuser.html', error="La contraseña debe tener al menos 6 caracteres")

        if edad < 1 or edad > 120:
            return render_template('newuser.html', error="Edad inválida")

        if genero not in ['M', 'F', 'O']:
            return render_template('newuser.html', error="Género inválido")

        # Verificar si el correo ya existe
        if Usuario.existe_correo(correo):
            return render_template('newuser.html', error="El correo electrónico ya está registrado")

        # Crear el usuario en la base de datos
        usuario_id = Usuario.crear_usuario(nombre, apellido, edad, genero, correo, clave)

        if usuario_id:
            # Registro exitoso, redirigir al login
            return render_template('login.html', success="Registro exitoso. Ya puedes iniciar sesión.")
        else:
            return render_template('newuser.html', error="Error al registrar el usuario. Intenta nuevamente.")

    except Exception as e:
        print(f"Error en el registro: {e}")
        return render_template('newuser.html', error="Error al procesar el registro")
