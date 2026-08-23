from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from datetime import datetime
from src.controllers.auth_controller import login_required, rol_required

cliente_bp = Blueprint('clientes', __name__)


def _client():
    return APIClient(session.get('api_token'))

@cliente_bp.route('/')
@login_required
@rol_required('Administrador', 'Vendedor')


# def index():
#     q = request.args.get('q', '').strip()
#     try:
#         data = _client().get('/clientes/')
#         print(f"data: {data}")  # Debugging line to check the structure of the response
#         clientes = APIClient.as_list(data)
#     except APIError as e:        
#         clientes = []

#     print(clientes)  # Debugging line to check the structure of the response
#     return render_template('Clientes/VerClientes.html', clientes=clientes, q=q)


def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 10}
        if q:
            params['q'] = q  
    
        data = _client().get('/clientes/', params=params)   # <-- ESTA ES LA LÍNEA MODIFICADA
        print(f"data: {data}")  # Debugging line to check the structure of the response
        clientes = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1
        
    except Exception as e:
        clientes = []

    print(clientes)  # Debugging line to check the structure of the response
    return render_template('clientes/VerClientes.html', clientes=clientes, meta=meta)


@cliente_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador', 'Vendedor')
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        edad = request.form.get('edad')
        correo = request.form.get('correo')
        documentoIdentidad = request.form.get('documentoIdentidad')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        FechaDeNacimiento = request.form.get('FechaDeNacimiento')
        
    # fecha_str = request.form.get('FechaDeNacimiento') 
    # # Lo conviertes a un objeto datetime real de Python
    # fecha_objeto = None
    # if fecha_str:
    #     fecha_objeto = datetime.fromisoformat(fecha_str)

        try:
            _client().post('/clientes/', json={ 
                'nombre': nombre,
                'apellido': apellido,
                'edad': edad,
                'correo': correo,
                'documentoIdentidad': documentoIdentidad,
                'direccion': direccion,
                'telefono': telefono,
                'FechaDeNacimiento': FechaDeNacimiento
            })  
            
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
        except APIError as e:
            flash(f'Error al crear cliente: {e.message}', 'danger')

    return render_template('Clientes/FormClientes.html')





