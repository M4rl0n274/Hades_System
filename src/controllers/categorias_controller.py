from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

categoria_bp = Blueprint('categorias', __name__)


def _client():
    return APIClient(session.get('api_token'))


@categoria_bp.route('/')
@login_required
@rol_required('Administrador', 'Vendedor')
def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 10}
        if q:
            params['q'] = q

        data = _client().get('/categorias/', params=params)
        categorias = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}

        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1

    except Exception as e:
        categorias = []

    return render_template('categorias/VerCategoria.html', categorias=categorias, meta=meta)


@categoria_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def nuevo():
    if request.method == 'POST':
        nombre_categoria = request.form.get('nombre_categoria', '').strip()

        if not nombre_categoria:
            flash('El nombre de la categoría es obligatorio', 'danger')
            return render_template('categorias/FormCategoria.html')

        try:
            # Enviamos 'nombre' ya que categorias_routes.py consume data['nombre']
            _client().post('/categorias/', json={
                'nombre': nombre_categoria
            })
            flash('Categoría creada exitosamente', 'success')
            return redirect(url_for('categorias.index'))
        except APIError as e:
            flash(f'Error al crear la categoría: {e.message}', 'danger')

    return render_template('categorias/FormCategoria.html')


@categoria_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def editar(id):
    if request.method == 'POST':
        nombre_categoria = request.form.get('nombre_categoria', '').strip()

        if not nombre_categoria:
            flash('El nombre de la categoría es obligatorio', 'danger')
            return redirect(url_for('categorias.editar', id=id))

        try:
            _client().put(f'/categorias/{id}', json={
                'nombre': nombre_categoria
            })
            flash('Categoría actualizada exitosamente', 'success')
            return redirect(url_for('categorias.index'))
        except APIError as e:
            flash(f'Error al actualizar la categoría: {e.message}', 'danger')

    try:
        categoria_actual = _client().get(f'/categorias/{id}')
    except APIError as e:
        flash(f'Error al cargar la categoría: {e.message}', 'danger')
        return redirect(url_for('categorias.index'))

    return render_template('categorias/EditarCategoria.html', categoria=categoria_actual)


@categoria_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador')
def eliminar(id):
    try:
        _client().delete(f'/categorias/{id}')
        flash('Categoría eliminada exitosamente', 'success')
    except APIError as e:
        flash(f'Error al eliminar la categoría: {e.message}', 'danger')

    return redirect(url_for('categorias.index'))