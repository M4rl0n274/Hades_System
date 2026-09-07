from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

factura_bp = Blueprint('facturas', __name__)


def _client():
    return APIClient(session.get('api_token'))

@factura_bp.route('/')
@login_required
@rol_required('Administrador')
# def index():
#     q = request.args.get('q', '').strip()
#     try:
#         data = _client().get('/factura/')
#         facturas = APIClient.as_list(data)
#     except APIError as e:        
#         facturas = []
        
#     return render_template('facturas/VerFacturas.html', facturas=facturas, q=q)


def index():
    q = request.args.get('q', '').strip()
    meta = {}
    page = request.args.get('page', 1, type=int)

    try:
        params = {'page': page, 'per_page': 8}
        if q:
            params['q'] = q  
    
        data = _client().get('/factura/', params=params)   # <-- ESTA ES LA LÍNEA MODIFICADA
        print(f"data: {data}")  # Debugging line to check the structure of the response
        facturas = APIClient.as_list(data)
        meta = data.get('meta', {}) if isinstance(data, dict) else {}
        
        if meta:
            meta['pages'] = meta.get('total_pages', meta.get('pages', 1))
            meta['prev_num'] = meta.get('page', 1) - 1
            meta['next_num'] = meta.get('page', 1) + 1
        
    except Exception as e:
        facturas = []

    print(facturas)  # Debugging line to check the structure of the response
    return render_template('facturas/VerFacturas.html', facturas=facturas, meta=meta)


@factura_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def nuevo():
    if request.method == 'POST':
        try:
           
            id_cliente = int(request.form.get('id_cliente'))
            id_vendedor = int(request.form.get('id_vendedor'))
            id_usuario = int(request.form.get('id_usuario'))


            id_productos = request.form.getlist('id_producto[]')
            cantidades = request.form.getlist('cantidad[]')

            #* Detalle necesario para la factura
            detalle = []
            for p_id, cant in zip(id_productos, cantidades):
                if p_id and cant:
                    detalle.append({
                        'id_producto': int(p_id),
                        'cantidad': int(cant)
                    })

            # Validar que al menos haya un producto agregado
            if not detalle:
                flash('Debe agregar al menos un producto a la factura', 'warning')
                return render_template('facturas/FormFacturas.html')

            # Petición a la API
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
            flash('Asegúrese de ingresar valores numéricos válidos.', 'danger')
        except APIError as e:
            flash(f'Error al crear factura: {e.message}', 'danger')


# ========== CARGA DE DATOS PARA LOS MENÚS DESPLEGABLES ==========
    try:
        clientes = APIClient.as_list(_client().get('/clientes/', params={'per_page': 1000}))
        vendedores = APIClient.as_list(_client().get('/vendedores/', params={'per_page': 1000}))
        usuarios = APIClient.as_list(_client().get('/usuarios/', params={'per_page': 1000}))
        productos = APIClient.as_list(_client().get('/productos/', params={'per_page': 1000}))
    except APIError as e:
        flash(f'Error al cargar datos para el formulario: {e.message}', 'danger')
        clientes, vendedores, usuarios, productos = [], [], [], []

    return render_template('facturas/FormFacturas.html', 
                            clientes=clientes, 
                            vendedores=vendedores, 
                            usuarios=usuarios, 
                            productos=productos)








#* RUTAS  PARA EDITAR Y ELIMINAR FACTURAS


@factura_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador')
def editar(id):
    if request.method == 'POST':
        # Nota: La lógica de actualización de productos requiere enviar los detalles modificados.
        id_cliente = int(request.form.get('id_cliente'))
        id_vendedor = int(request.form.get('id_vendedor'))
        id_usuario = int(request.form.get('id_usuario'))

        try:
            # Enviar actualización a la API (Requiere que crees el endpoint PUT en el backend)
            _client().put(f'/factura/{id}', json={ 
                'id_cliente': id_cliente,
                'id_vendedor': id_vendedor,
                'id_usuario': id_usuario
            })  
            flash('Factura actualizada exitosamente', 'success')
            return redirect(url_for('facturas.index'))
        except APIError as e:
            flash(f'Error al actualizar la factura: {e.message}', 'danger')

    try:
        factura_actual = _client().get(f'/factura/{id}')
        # Traer listas para los menús desplegables (pasamos per_page=1000 para cargar todos)
        clientes = APIClient.as_list(_client().get('/clientes/', params={'per_page': 1000}))
        vendedores = APIClient.as_list(_client().get('/vendedores/', params={'per_page': 1000}))
        usuarios = APIClient.as_list(_client().get('/usuarios/', params={'per_page': 1000}))
    except APIError as e:
        flash(f'Error al cargar la factura: {e.message}', 'danger')
        return redirect(url_for('facturas.index'))

# Pasamos las listas al template
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