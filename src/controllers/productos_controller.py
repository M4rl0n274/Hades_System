from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

producto_bp = Blueprint('productos', __name__)


def _client():
    return APIClient(session.get('api_token'))

#* mostrar información
@producto_bp.route('/')
#* decorado para que el login sea requerido
@login_required


def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 10}
        if q:
            params['q'] = q  
    
        data = _client().get('/productos/', params=params)   # <-- ESTA ES LA LÍNEA MODIFICADA
        print(f"data: {data}")  # Debugging line to check the structure of the response
        productos = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1
        
    except Exception as e:
        productos = []

    print(productos)  # Debugging line to check the structure of the response
    return render_template('productos/VerproductosPaginada.html', productos=productos, meta=meta)





# #* Post de información
# @cliente_bp.route('/nuevo', methods=['GET', 'POST'])
# #* decorado para que el login sea requerido
# @login_required
# def nuevo():
#     if request.method == 'POST':
#         nombre = request.form.get('nombre')
#         email = request.form.get('email')
#         telefono = request.form.get('telefono')
#         direccion = request.form.get('direccion')
#         documento = request.form.get('documento')

#         try:
#             _client().post('/clientes/', json={
#                 'nombre': nombre,
#                 'email': email,
#                 'telefono': telefono,
#                 'direccion': direccion,
#                 'documento': documento
#             })
#             flash('Cliente creado exitosamente', 'success')
#             return redirect(url_for('clientes.index'))
#         except APIError as e:
#             flash(f'Error al crear cliente: {e.message}', 'danger')

#     return render_template('Clientes/form.html')