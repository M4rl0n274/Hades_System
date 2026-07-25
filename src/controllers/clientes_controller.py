from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from datetime import datetime

cliente_bp = Blueprint('clientes', __name__)


def _client():
    return APIClient(session.get('api_token'))

@cliente_bp.route('/')
def index():
    q = request.args.get('q', '').strip()
    try:
        data = _client().get('/clientes/')
        print(f"data: {data}")  # Debugging line to check the structure of the response
        clientes = APIClient.as_list(data)
    except APIError as e:        
        clientes = []

    print(clientes)  # Debugging line to check the structure of the response
    return render_template('Clientes/VerClientes.html', clientes=clientes, q=q)

@cliente_bp.route('/nuevo', methods=['GET', 'POST'])
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





