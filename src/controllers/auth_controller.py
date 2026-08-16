"""
Controlador de autenticación del frontend.

El frontend no valida credenciales: se las delega al backend y guarda
el token que este devuelve en la sesión de Flask (cookie firmada).
A partir de ahí, cada llamada al API lo reenvía en el header Authorization.
"""
from functools import wraps

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)

from src.clients.api_client import APIClient, APIError

auth_bp = Blueprint('auth', __name__)


# ---------------------------------------------------------------------------
# Decoradores
# ---------------------------------------------------------------------------

def login_required(f):
    """Exige sesión activa. Guarda la URL destino para volver tras el login."""
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get('api_token'):
            session['next_url'] = request.url
            flash('Debes iniciar sesión para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorada


def rol_required(*roles):
    """Se usa después de @login_required."""
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            usuario = session.get('usuario') or {}
            if usuario.get('rol') not in roles:
                flash('No tienes permisos para acceder a esa sección.', 'danger')
                return redirect(url_for('clientes.index'))
            return f(*args, **kwargs)
        return decorada
    return decorador


# ---------------------------------------------------------------------------
# Helpers de sesión
# ---------------------------------------------------------------------------

def cerrar_sesion(mensaje=None, categoria='info'):
    """Limpia la sesión local y redirige al login."""
    session.pop('api_token', None)
    session.pop('usuario', None)
    if mensaje:
        flash(mensaje, categoria)
    return redirect(url_for('auth.login'))


def sesion_expirada():
    """Atajo para cuando el API responde 401 en medio de la navegación."""
    return cerrar_sesion('Tu sesión expiró. Ingresa de nuevo.', 'warning')


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya hay sesión, no tiene sentido mostrar el formulario
    if session.get('api_token'):
         return redirect('index.html')

    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')

        if not correo or not password:
            flash('Correo y contraseña son obligatorios.', 'danger')
            return render_template('auth/login.html', correo=correo)

        try:
            # APIClient sin token: el login es la ruta pública
            data = APIClient().post('/auth/login', json={
                'correo': correo,
                'password': password
            })

            session['api_token'] = data['access_token']
            session['usuario'] = data['usuario']
            session.permanent = True

            # flash(f"Bienvenido, {data['usuario']['nombre']}.", 'success')

            # Vuelve a donde el usuario quería ir antes de que lo mandaran acá
            destino = session.pop('next_url', None)
            return redirect(destino or url_for('clientes.index'))

        except APIError as e:
            flash(e.message, 'danger')
            # Se devuelve el correo para no obligar a reescribirlo,
            # nunca la contraseña
            return render_template('auth/login.html', correo=correo)

    return render_template('auth/login.html', correo='')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """POST y no GET: un logout por GET se dispara con un <img> ajeno
    o con el prefetch del navegador."""
    return cerrar_sesion('Sesión cerrada correctamente.', 'success')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if session.get('api_token'):
        return redirect(url_for('clientes.index'))

    if request.method == 'POST':
        payload = {
            'nombre':   request.form.get('nombre', '').strip(),
            'correo':    request.form.get('correo', '').strip(),
            'password': request.form.get('password', ''),
        }
        confirmacion = request.form.get('password_confirmacion', '')

        if not all(payload.values()):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('auth/registro.html', datos=payload)

        if payload['password'] != confirmacion:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/registro.html', datos=payload)

        try:
            APIClient().post('/auth/register', json=payload)
            flash('Cuenta creada. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except APIError as e:
            flash(e.message, 'danger')
            return render_template('auth/registro.html', datos=payload)

    return render_template('auth/registro.html', datos={})


@auth_bp.route('/perfil')
@login_required
def perfil():
    try:
        usuario = APIClient(session['api_token']).get('/auth/me')
        # Refresca la copia local por si cambió el nombre o el rol
        session['usuario'] = usuario
    except APIError as e:
        if e.status_code == 401:
            return sesion_expirada()
        flash(e.message, 'danger')
        usuario = session.get('usuario', {})

    return render_template('auth/perfil.html', usuario=usuario)
