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
            rol_actual = usuario.get('rol')
            
            if rol_actual not in roles:
                flash('No tienes permisos para acceder a esa sección.', 'danger')
                
                # Redirección dinámica y segura para evitar ERR_TOO_MANY_REDIRECTS
                if rol_actual == 'Cliente':
                    return redirect(url_for('clientes.mis_facturas'))
                elif rol_actual == 'Usuario':
                    return redirect(url_for('productos.index'))
                elif rol_actual == 'Administrador':
                    return redirect(url_for('home.index'))
                else:
                    return redirect(url_for('auth.login'))
                    
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

# En src/controllers/auth_controller.py

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('api_token'):
        rol = session.get('usuario', {}).get('rol')
        if rol == 'Usuario':
            return redirect(url_for('productos.index'))
        elif rol == 'Cliente':
            return redirect(url_for('clientes.mis_facturas'))
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')

        if not correo or not password:
            flash('Correo y contraseña son obligatorios.', 'danger')
            return render_template('auth/login.html', correo=correo)

        try:
            data = APIClient().post('/auth/login', json={
                'correo': correo,
                'password': password
            })

            session['api_token'] = data['access_token']
            session['usuario'] = data['usuario']
            session.permanent = True

            destino = session.pop('next_url', None)
            rol = data['usuario'].get('rol')

            # Redirección dinámica por rol
            if rol == 'Usuario':
                return redirect(url_for('productos.index'))
            elif rol == 'Cliente':
                return redirect(url_for('clientes.mis_facturas'))
            
            return redirect(destino or url_for('home.index'))

        except APIError as e:
            flash(e.message, 'danger')
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
            'nombre': request.form.get('nombre', '').strip(),
            'apellido': request.form.get('apellido', '').strip(),
            'documento_identidad': request.form.get('documento_identidad', '').strip(),
            'correo': request.form.get('correo', '').strip(),
            'password': request.form.get('password', ''),
            'rol': 'Usuario'  # Rol asignado automáticamente por seguridad
        }
        confirmacion = request.form.get('password_confirmacion', '')

        # Validamos que todos los campos del payload tengan valor
        if not all([payload['nombre'], payload['apellido'], payload['documento_identidad'], payload['correo'], payload['password']]):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('auth/registro.html', datos=payload)

        if payload['password'] != confirmacion:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/registro.html', datos=payload)

        try:
            APIClient().post('/auth/register', json=payload)
            flash('Cuenta creada exitosamente. Ya puedes iniciar sesión.', 'success')
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
