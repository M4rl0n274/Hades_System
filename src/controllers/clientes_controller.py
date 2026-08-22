from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

cliente_bp = Blueprint('clientes', __name__)


def _client():
    return APIClient(session.get('api_token'))

#* mostrar información
@cliente_bp.route('/')
#* decorado para que el login sea requerido
@login_required
def index():
    q = request.args.get('q', '').strip()
    try:
        
        
        data = _client().get('/clientes/')
        print(f"data: {data}")  # Debugging line to check the structure of the response
        clientes = APIClient.as_list(data)
    except APIError as e:        
        clientes = []

    print(clientes)  # Debugging line to check the structure of the response
    return render_template('clientes/verClientes.html', clientes=clientes, q=q)

#* Post de información
@cliente_bp.route('/nuevo', methods=['GET', 'POST'])
#* decorado para que el login sea requerido
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        documento = request.form.get('documento')

        try:
            _client().post('/clientes/', json={
                'nombre': nombre,
                'email': email,
                'telefono': telefono,
                'direccion': direccion,
                'documento': documento
            })
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
        except APIError as e:
            flash(f'Error al crear cliente: {e.message}', 'danger')

    return render_template('Clientes/form.html')