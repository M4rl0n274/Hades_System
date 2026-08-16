from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from datetime import datetime
from src.controllers.auth_controller import login_required, rol_required

producto_bp = Blueprint('productos', __name__)


def _client():
    return APIClient(session.get('api_token'))

@producto_bp.route('/')
@login_required
@rol_required('Administrador', 'Vendedor')
def index():
    q = request.args.get('q', '').strip()
    try:
        data = _client().get('/productos/')
        print(f"data: {data}")  # Debugging line to check the structure of the response
        productos = APIClient.as_list(data)
    except APIError as e:        
        productos = []

    print(productos)  # Debugging line to check the structure of the response
    return render_template('productos/VerProducto.html', productos=productos, q=q)

@producto_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador', 'Vendedor')
def nuevo():
    if request.method == 'POST':
        id_categoria = request.form.get('id_categoria')
        nombre_producto = request.form.get('nombre_producto')
        descripcion = request.form.get('descripcion')
        valor_unitario = request.form.get('valor_unitario')
        stock = request.form.get('stock')    
        codigo = request.form.get('codigo')
   
    # fecha_str = request.form.get('FechaDeNacimiento') 
    # # Lo conviertes a un objeto datetime real de Python
    # fecha_objeto = None
    # if fecha_str:
    #     fecha_objeto = datetime.fromisoformat(fecha_str)

        try:
            _client().post('/productos/', json={ 
                'id_categoria': id_categoria,    
                'nombre_producto': nombre_producto,
                'descripcion': descripcion,
                'valor_unitario': valor_unitario,
                'stock': stock,
                'codigo': codigo,

            })  
            
            flash('producto creado exitosamente', 'success')
            return redirect(url_for('productos.index'))
        except APIError as e:
            flash(f'Error al crear cliente: {e.message}', 'danger')

    return render_template('productos/FormProductos.html')





