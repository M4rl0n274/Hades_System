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
        
        # ==========================================
        # LIMPIEZA DE FECHAS PARA LA TABLA
        # ==========================================
        for cliente in clientes:
            fecha_api = cliente.get('FechaDeNacimiento')
            if fecha_api:
                try:
                    if "GMT" in str(fecha_api):
                        dt = datetime.strptime(fecha_api, "%a, %d %b %Y %H:%M:%S GMT")
                        # Formato YYYY-MM-DD. Si prefieres DD/MM/YYYY cambia a "%d/%m/%Y"
                        cliente['FechaDeNacimiento'] = dt.strftime("%Y-%m-%d") 
                    else:
                        cliente['FechaDeNacimiento'] = str(fecha_api)[:10]
                except Exception:
                    pass
    
     
        
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
@rol_required('Administrador')
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
        password = request.form.get('password')  # <-- Captura la contraseña ingresada

        payload = {
            'nombre': nombre,
            'apellido': apellido,
            'edad': edad,
            'correo': correo,
            'documentoIdentidad': documentoIdentidad,
            'direccion': direccion,
            'telefono': telefono,
            'FechaDeNacimiento': FechaDeNacimiento
        }

        # Incluye la contraseña si fue diligenciada en el formulario
        if password and password.strip() != '':
            payload['password'] = password.strip()

        try:
            _client().post('/clientes/', json=payload)
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
        except APIError as e:
            flash(f'Error al crear cliente: {e.message}', 'danger')

    return render_template('Clientes/FormClientes.html')



# PARA EDITAR Y ELIMINAR CLIENTES


@cliente_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def editar(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        edad = request.form.get('edad', type=int)
        correo = request.form.get('correo')
        documentoIdentidad = request.form.get('documentoIdentidad')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        FechaDeNacimiento = request.form.get('FechaDeNacimiento')
        password = request.form.get('password')  # <-- Captura opcional al editar

        payload = {
            'nombre': nombre,
            'apellido': apellido,
            'edad': edad,
            'correo': correo,
            'documentoIdentidad': documentoIdentidad,
            'direccion': direccion,
            'telefono': telefono,
            'FechaDeNacimiento': FechaDeNacimiento
        }

        # Solo envía la contraseña al backend si fue modificada
        if password and password.strip() != '':
            payload['password'] = password.strip()

        try:
            _client().put(f'/clientes/{id}', json=payload)
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
        except APIError as e:
            flash(f'Error al actualizar el cliente: {e.message}', 'danger')

    # Carga de datos del cliente en GET para llenar la vista de edición
    try:
        cliente = _client().get(f'/clientes/{id}')
        return render_template('Clientes/EditarCliente.html', cliente=cliente)
    except APIError as e:
        flash(f'Error al obtener datos del cliente: {e.message}', 'danger')
        return redirect(url_for('clientes.index'))



# Método GET: Cargar los datos actuales del cliente
    try:
        cliente_actual = _client().get(f'/clientes/{id}')
        
        # ==========================================
        # CORRECCIÓN PARA EL FORMATO DE LA FECHA
        # ==========================================
        fecha_api = cliente_actual.get('FechaDeNacimiento')
        if fecha_api:
            try:
                # Si Flask/JSON devuelve formato web estándar: "Wed, 02 Nov 2022 00:00:00 GMT"
                if "GMT" in str(fecha_api):
                    dt = datetime.strptime(fecha_api, "%a, %d %b %Y %H:%M:%S GMT")
                    cliente_actual['FechaDeNacimiento'] = dt.strftime("%Y-%m-%d")
                else:
                    # Si viene como ISO "2022-11-02 00:00:00" o "2022-11-02T00:00:00"
                    # Cortamos solo los primeros 10 caracteres (YYYY-MM-DD)
                    cliente_actual['FechaDeNacimiento'] = str(fecha_api)[:10]
            except Exception:
                # Si ocurre un error al procesar, lo dejamos como viene para evitar que se caiga la app
                pass
        # ==========================================
        
    except APIError as e:
        flash(f'Error al cargar el cliente: {e.message}', 'danger')
        return redirect(url_for('clientes.index'))

    return render_template('Clientes/EditarCliente.html', cliente=cliente_actual)




    

@cliente_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador')
def eliminar(id):
    try:
        _client().delete(f'/clientes/{id}')
        flash('Cliente eliminado exitosamente', 'success')
    except APIError as e:
        flash(f'Error al eliminar el cliente: {e.message}', 'danger')
        
    return redirect(url_for('clientes.index'))



# Ruta para que el cliente vea sus facturas asociadas
@cliente_bp.route('/mis-facturas')
@login_required
@rol_required('Cliente')
def mis_facturas():
    usuario = session.get('usuario', {})
    id_cliente = usuario.get('id')
    page = request.args.get('page', 1, type=int)

    try:
        # Filtrar facturas enviando el ID del cliente autenticado a la API
        params = {'id_cliente': id_cliente, 'page': page, 'per_page': 8}
        data = _client().get('/factura/', params=params)
        
        facturas = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1

        # Resumen financiero personal del cliente
        total_comprado = sum(float(f.get('total', 0)) for f in facturas)

    except Exception:
        facturas = []
        meta = {}
        total_comprado = 0

    return render_template('clientes/MisFacturas.html', 
                           cliente=usuario, 
                           facturas=facturas, 
                           meta=meta, 
                           total_comprado=total_comprado)
