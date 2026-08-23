from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from datetime import datetime
from src.controllers.auth_controller import login_required, rol_required

vendedores_bp = Blueprint('vendedores', __name__)


def _client():
    return APIClient(session.get('api_token'))

@vendedores_bp.route('/')
@login_required
@rol_required('Administrador')


# def index():
#     q = request.args.get('q', '').strip()
#     try:
#         data = _client().get('/vendedores/')
#         print(f"data: {data}")  # Debugging line to check the structure of the response
#         vendedores = APIClient.as_list(data)
#     except APIError as e:        
#         vendedores = []

#     print(vendedores)  # Debugging line to check the structure of the response
#     return render_template('vendedores/VerVendedores.html', vendedores=vendedores, q=q)


def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 10}
        if q:
            params['q'] = q  
    
        data = _client().get('/vendedores/', params=params)   # <-- ESTA ES LA LÍNEA MODIFICADA
        print(f"data: {data}")  # Debugging line to check the structure of the response
        vendedores = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1
        
    except Exception as e:
        vendedores = []

    print(vendedores)  # Debugging line to check the structure of the response
    return render_template('vendedores/VerVendedores.html', vendedores=vendedores, meta=meta)



@vendedores_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        documento_identidad = request.form.get('documento_identidad')
        correo = request.form.get('correo')

        
    # fecha_str = request.form.get('FechaDeNacimiento') 
    # # Lo conviertes a un objeto datetime real de Python
    # fecha_objeto = None
    # if fecha_str:
    #     fecha_objeto = datetime.fromisoformat(fecha_str)

        try:
            _client().post('/vendedores/', json={ 
                'nombre': nombre,
                'apellido': apellido,
                'documento_identidad': documento_identidad,
                'correo': correo,

            })  
            
            flash('Vendedor creado exitosamente', 'success')
            return redirect(url_for('vendedores.index'))
        except APIError as e:
            flash(f'Error al crear vendedor: {e.message}', 'danger')

    return render_template('vendedores/FormVendedores.html')





