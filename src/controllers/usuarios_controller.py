from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

usuarios_bp = Blueprint('usuarios', __name__)


def _client():
    return APIClient(session.get('api_token'))


@usuarios_bp.route('/')
@login_required
@rol_required('Administrador')
def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 8}
        if q:
            params['q'] = q

        data = _client().get('/usuarios/', params=params)
        usuarios = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}

        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1

    except Exception:
        usuarios = []

    return render_template('usuarios/VerUsuarios.html', usuarios=usuarios, meta=meta)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        correo = request.form.get('correo', '').strip()
        documento_identidad = request.form.get('documento_identidad', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', '').strip()

        if not all([nombre, apellido, correo, documento_identidad, password, rol]):
            flash('Todos los campos son obligatorios.', 'warning')
            return render_template('usuarios/FormUsuarios.html')

        try:
            _client().post('/usuarios/', json={
                'nombre': nombre,
                'apellido': apellido,
                'correo': correo,
                'documento_identidad': documento_identidad,
                'password': password,
                'rol': rol
            })

            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
        except APIError as e:
            flash(f'Error al crear usuario: {e.message}', 'danger')

    return render_template('usuarios/FormUsuarios.html')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def editar(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        correo = request.form.get('correo', '').strip()
        documento_identidad = request.form.get('documento_identidad', '').strip()
        rol = request.form.get('rol', '').strip()
        password = request.form.get('password', '')

        payload = {
            'nombre': nombre,
            'apellido': apellido,
            'correo': correo,
            'documento_identidad': documento_identidad,
            'rol': rol
        }
        
        # Solo se envía la contraseña si fue proporcionada en el formulario
        if password:
            payload['password'] = password

        try:
            _client().put(f'/usuarios/{id}', json=payload)
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.index'))
        except APIError as e:
            flash(f'Error al actualizar usuario: {e.message}', 'danger')

    try:
        usuario_actual = _client().get(f'/usuarios/{id}')
    except APIError as e:
        flash(f'Error al cargar el usuario: {e.message}', 'danger')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/EditarUsuario.html', usuario=usuario_actual)


@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador')
def eliminar(id):
    try:
        _client().delete(f'/usuarios/{id}')
        flash('Usuario eliminado exitosamente', 'success')
    except APIError as e:
        flash(f'Error al eliminar el usuario: {e.message}', 'danger')

    return redirect(url_for('usuarios.index'))