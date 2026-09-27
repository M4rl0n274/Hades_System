from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

factura_bp = Blueprint('facturas', __name__)


def _client():
    return APIClient(session.get('api_token'))


@factura_bp.route('/')
@login_required
@rol_required('Administrador', 'Vendedor')
def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 8}
        if q:
            params['q'] = q  
    
        data = _client().get('/factura/', params=params)
        facturas = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1
        
    except Exception:
        facturas = []

    return render_template('facturas/VerFacturas.html', facturas=facturas, meta=meta)


@factura_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador', 'Vendedor')
def nuevo():
    if request.method == 'POST':
        try:
            id_cliente = int(request.form.get('id_cliente'))
            id_vendedor = int(request.form.get('id_vendedor'))
            
            # Se asigna automáticamente el usuario en sesión
            usuario_sesion = session.get('usuario', {})
            id_usuario = usuario_sesion.get('id') or int(request.form.get('id_usuario'))

            id_productos = request.form.getlist('id_producto[]')
            cantidades = request.form.getlist('cantidad[]')

            detalle = []
            for p_id, cant in zip(id_productos, cantidades):
                if p_id and cant:
                    detalle.append({
                        'id_producto': int(p_id),
                        'cantidad': int(cant)
                    })

            if not detalle:
                flash('Debe agregar al menos un producto a la factura', 'warning')
                return redirect(url_for('facturas.nuevo'))

            payload = { 
                'id_cliente': id_cliente,
                'id_vendedor': id_vendedor,
                'id_usuario': id_usuario,
                'detalle': detalle
            }

            _client().post('/factura/', json=payload)  
            
            flash('Factura creada exitosamente', 'success')
            return redirect(url_for('facturas.index'))

        except ValueError:
            flash('Asegúrese de seleccionar cliente, vendedor e ingresar cantidades válidas.', 'danger')
        except APIError as e:
            flash(f'Error al crear factura: {e.message}', 'danger')

    return render_template('facturas/FormFacturas.html')


# ========== ENDPOINTS AJAX PARA BÚSQUEDA MODAL DE ENTIDADES ==========

@factura_bp.route('/api/productos', methods=['GET'])
@login_required
def api_productos():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    try:
        params = {'page': page, 'per_page': per_page}
        if q:
            params['q'] = q

        data = _client().get('/productos/', params=params)
        return jsonify(data), 200
    except APIError as e:
        return jsonify({'data': [], 'meta': {}, 'message': e.message}), 400


@factura_bp.route('/api/clientes', methods=['GET'])
@login_required
def api_clientes():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    try:
        params = {'page': page, 'per_page': per_page}
        if q:
            params['q'] = q

        data = _client().get('/clientes/', params=params)
        return jsonify(data), 200
    except APIError as e:
        return jsonify({'data': [], 'meta': {}, 'message': e.message}), 400


@factura_bp.route('/api/vendedores', methods=['GET'])
@login_required
def api_vendedores():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    try:
        params = {'page': page, 'per_page': per_page}
        if q:
            params['q'] = q

        data = _client().get('/vendedores/', params=params)
        return jsonify(data), 200
    except APIError as e:
        return jsonify({'data': [], 'meta': {}, 'message': e.message}), 400


@factura_bp.route('/<int:id>/json', methods=['GET'])
@login_required
@rol_required('Administrador', 'Vendedor', 'Cliente')
def obtener_json(id):
    try:
        factura_data = _client().get(f'/factura/{id}')
        return jsonify(factura_data), 200
    except APIError as e:
        return jsonify({'message': e.message}), 400


@factura_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def editar(id):
    if request.method == 'POST':
        id_cliente = int(request.form.get('id_cliente'))
        id_vendedor = int(request.form.get('id_vendedor'))
        id_usuario = int(request.form.get('id_usuario'))

        try:
            _client().put(f'/factura/{id}', json={ 
                'id_cliente': id_cliente,
                'id_vendedor': id_vendedor,
                'id_usuario': id_usuario
            })  
            flash('Factura actualizada exitosamente', 'success')
            return redirect(url_for('facturas.editar', id=id))
        except APIError as e:
            flash(f'Error al actualizar la factura: {e.message}', 'danger')

    try:
        factura_actual = _client().get(f'/factura/{id}')
        clientes = APIClient.as_list(_client().get('/clientes/', params={'per_page': 1000}))
        vendedores = APIClient.as_list(_client().get('/vendedores/', params={'per_page': 1000}))
        usuarios = APIClient.as_list(_client().get('/usuarios/', params={'per_page': 1000}))
    except APIError as e:
        flash(f'Error al cargar la factura: {e.message}', 'danger')
        return redirect(url_for('facturas.index'))

    return render_template('facturas/EditarFactura.html', 
                           factura=factura_actual,
                           clientes=clientes,
                           vendedores=vendedores,
                           usuarios=usuarios)


@factura_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador')
def eliminar(id):
    try:
        _client().delete(f'/factura/{id}')
        flash('Factura eliminada exitosamente', 'success')
    except APIError as e:
        flash(f'Error al eliminar la factura: {e.message}', 'danger')
        
    return redirect(url_for('facturas.index'))


@factura_bp.route('/detalle/<int:id_detalle>/actualizar', methods=['POST'])
@login_required
@rol_required('Administrador')
def actualizar_detalle(id_detalle):
    id_factura = request.form.get('id_factura')
    cantidad = request.form.get('cantidad', type=int)

    try:
        _client().put(f'/detalle_factura/{id_detalle}', json={
            'cantidad': cantidad
        })
        flash('Cantidad del producto actualizada exitosamente', 'success')
    except APIError as e:
        flash(f'Error al actualizar el producto: {e.message}', 'danger')

    return redirect(url_for('facturas.editar', id=id_factura))


@factura_bp.route('/detalle/<int:id_detalle>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador')
def eliminar_detalle(id_detalle):
    id_factura = request.form.get('id_factura')
    try:
        _client().delete(f'/detalle_factura/{id_detalle}')
        flash('Producto removido de la factura', 'success')
    except APIError as e:
        flash(f'Error al quitar el producto: {e.message}', 'danger')

    return redirect(url_for('facturas.editar', id=id_factura))