from flask import render_template, request, redirect, url_for, flash, session
from app import app
from app.models import Usuario
from functools import wraps
import sys
from pathlib import Path

# Agregar la carpeta ml al path para importar el predictor
sys.path.insert(0, str(Path(__file__).parent.parent / 'ml'))
from predict import predictor

# Decorador para rutas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
            # Si todo está bien, guardar en sesión y llevar al usuario al index
            session['usuario_id'] = 0  # ID ficticio para usuarios de prueba
            session['nombre'] = username
            return redirect(url_for('index'))

        # Si no está en usuarios de prueba, verificar en la base de datos
        # Intentar con el username como correo electrónico
        usuario_db = Usuario.verificar_credenciales(username, password)

        if usuario_db:
            # Credenciales válidas desde la base de datos
            session['usuario_id'] = usuario_db['id']
            session['nombre'] = usuario_db['nombre']
            session['correo'] = usuario_db['correo']
            return redirect(url_for('index'))
        else:
            # Si las credenciales son incorrectas, muestra el error
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    # Si es GET, solo muestra el formulario
    return render_template('login.html')

@app.route('/index')
@login_required
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

@app.route('/cuenta')
@login_required
def cuenta():
    """Muestra la página de cuenta del usuario"""
    usuario_id = session.get('usuario_id')

    # Si es usuario de prueba (ID 0), mostrar datos básicos
    if usuario_id == 0:
        usuario = {
            'nombre': session.get('nombre', ''),
            'apellido': 'N/A',
            'edad': 0,
            'genero': 'N/A',
            'correo': 'N/A',
            'grado_escolaridad': None,
            'fecha_nacimiento': None
        }
    else:
        # Obtener datos del usuario desde la base de datos
        usuario = Usuario.obtener_por_id(usuario_id)

        if not usuario:
            flash('Error al cargar los datos del usuario', 'error')
            return redirect(url_for('index'))

    return render_template('cuenta.html', usuario=usuario)

@app.route('/actualizar_cuenta', methods=['POST'])
@login_required
def actualizar_cuenta():
    """Actualiza los datos de la cuenta del usuario"""
    try:
        usuario_id = session.get('usuario_id')

        # No permitir actualización para usuarios de prueba
        if usuario_id == 0:
            flash('Los usuarios de prueba no pueden actualizar su perfil', 'warning')
            return redirect(url_for('cuenta'))

        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        edad = request.form.get('edad', type=int)
        genero = request.form.get('genero', '')
        correo = request.form.get('correo', '').strip().lower()
        grado_escolaridad = request.form.get('grado_escolaridad', '').strip() or None
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip() or None

        # Validaciones
        if not all([nombre, apellido, edad, genero, correo]):
            flash('Los campos básicos son obligatorios', 'error')
            return redirect(url_for('cuenta'))

        if edad < 1 or edad > 120:
            flash('Edad inválida', 'error')
            return redirect(url_for('cuenta'))

        if genero not in ['M', 'F', 'O']:
            flash('Género inválido', 'error')
            return redirect(url_for('cuenta'))

        # Verificar si el correo ya existe (y no es el mismo usuario)
        usuario_actual = Usuario.obtener_por_id(usuario_id)
        if correo != usuario_actual['correo'] and Usuario.existe_correo(correo):
            flash('El correo electrónico ya está registrado por otro usuario', 'error')
            return redirect(url_for('cuenta'))

        # Actualizar el usuario
        resultado = Usuario.actualizar_usuario(
            usuario_id, nombre, apellido, edad, genero, correo,
            grado_escolaridad, fecha_nacimiento
        )

        if resultado:
            # Actualizar datos en la sesión
            session['nombre'] = nombre
            session['correo'] = correo
            flash('Perfil actualizado correctamente', 'success')
        else:
            flash('Error al actualizar el perfil', 'error')

        return redirect(url_for('cuenta'))

    except Exception as e:
        print(f"Error al actualizar cuenta: {e}")
        flash('Error al procesar la actualización', 'error')
        return redirect(url_for('cuenta'))

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('inicio'))

@app.route('/procesar_formulario', methods=['POST'])
@login_required
def procesar_formulario():
    """Procesa el formulario y genera la prediccion"""
    try:
        usuario_id = session.get('usuario_id')

        # Obtener datos del formulario
        datos_formulario = {
            'daily_usage': request.form.get('daily_usage'),
            'sleephours': request.form.get('sleephours'),
            'academic_perf': request.form.get('academic_perf'),
            'exercise': request.form.get('exercise'),
            'screen_before_bed': request.form.get('screen_before_bed'),
            'checks_per_day': request.form.get('checks_per_day'),
            'apps_daily': request.form.getlist('apps_daily'),  # Multiple select
            'time_social_media': request.form.get('time_social_media'),
            'time_gaming': request.form.get('time_gaming'),
            'time_education': request.form.get('time_education'),
            'purpose': request.form.get('purpose'),
            'weekend_usage': request.form.get('weekend_usage')
        }

        # Obtener datos de la cuenta si existe
        datos_cuenta = None
        if usuario_id and usuario_id != 0:
            usuario = Usuario.obtener_por_id(usuario_id)
            if usuario:
                datos_cuenta = {
                    'edad': usuario['edad'],
                    'genero': usuario['genero'],
                    'grado_escolaridad': usuario.get('grado_escolaridad')
                }

        # Realizar prediccion
        resultado = predictor.predecir(datos_formulario, datos_cuenta)

        # Guardar resultado en sesion para mostrarlo
        session['ultimo_resultado'] = resultado

        return redirect(url_for('resultados'))

    except Exception as e:
        print(f"Error al procesar formulario: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al procesar el formulario. Intenta nuevamente.', 'error')
        return redirect(url_for('formulario'))

@app.route('/resultados')
@login_required
def resultados():
    """Muestra los resultados de la prediccion"""
    resultado = session.get('ultimo_resultado')

    if not resultado:
        flash('No hay resultados disponibles. Completa el formulario primero.', 'warning')
        return redirect(url_for('formulario'))

    return render_template('resultados.html', resultado=resultado)
