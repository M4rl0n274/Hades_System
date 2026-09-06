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
# def index():
#     q = request.args.get('q', '').strip()
#     try:
#         data = _client().get('/productos/')
#         print(f"data: {data}")  # Debugging line to check the structure of the response
#         productos = APIClient.as_list(data)
#     except APIError as e:        
#         productos = []

#     print(productos)  # Debugging line to check the structure of the response
#     return render_template('productos/VerProducto.html', productos=productos, q=q)


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
    return render_template('productos/Verproducto.html', productos=productos, meta=meta)




@producto_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador', 'Vendedor')
def nuevo():
    if request.method == 'POST':
        id_categoria = request.form.get('id_categoria', type=int)
        nombre_producto = request.form.get('nombre_producto')
        descripcion = request.form.get('descripcion')
        valor_unitario = request.form.get('valor_unitario', type=float)
        stock = request.form.get('stock', type=int)    
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
            
            
# ========== CÓDIGO NUEVO PARA CARGAR CATEGORÍAS EN MÉTODO GET ==========
    try:
        data_categorias = _client().get('/categorias/') 
        categorias = APIClient.as_list(data_categorias) # Adaptado a tu método actual
    except Exception as e:
        categorias = [] # Si hay error, envía una lista vacía
        
    return render_template('productos/FormProductos.html', categorias=categorias)













@producto_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@rol_required('Administrador') # Requerido según el backend para hacer PUT
def editar(id):
    if request.method == 'POST':
        # 1. Recuperar los datos del formulario (Actualizar)
        id_categoria = request.form.get('id_categoria', type=int)
        nombre_producto = request.form.get('nombre_producto')
        descripcion = request.form.get('descripcion')
        valor_unitario = request.form.get('valor_unitario', type=float)
        stock = request.form.get('stock', type=int)    
        codigo = request.form.get('codigo')

        try:
            # Enviar solicitud PUT a la API
            _client().put(f'/productos/{id}', json={ 
                'id_categoria': id_categoria,    
                'nombre_producto': nombre_producto,
                'descripcion': descripcion,
                'valor_unitario': valor_unitario,
                'stock': stock,
                'codigo': codigo
            })  
            
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('productos.index'))
        except APIError as e:
            flash(f'Error al actualizar el producto: {e.message}', 'danger')

    # 2. Si es método GET, cargar los datos actuales del producto para llenar el formulario
    try:
        producto_actual = _client().get(f'/productos/{id}')
    except APIError as e:
        flash(f'Error al cargar el producto: {e.message}', 'danger')
        return redirect(url_for('productos.index'))

    # Retorna a un formulario, pasando el "producto_actual". 
    # Nota: Puedes re-utilizar 'FormProductos.html' si lo configuras para recibir un producto, 
    # o crear un archivo nuevo llamado 'EditarProducto.html'.
    
    
    
    # ========== CÓDIGO NUEVO PARA CARGAR CATEGORÍAS EN MÉTODO GET ==========
    try:
        producto_actual = _client().get(f'/productos/{id}')
        # Consultamos también las categorías
        data_categorias = _client().get('/categorias/')
        categorias = APIClient.as_list(data_categorias)
    except APIError as e:
        flash(f'Error al cargar datos: {e.message}', 'danger')
        return redirect(url_for('productos.index'))

    return render_template('productos/EditarProducto.html', producto=producto_actual, categorias=categorias)



@producto_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@rol_required('Administrador') # Requerido según el backend para hacer DELETE
def eliminar(id):
    try:
        _client().delete(f'/productos/{id}')
        flash('Producto eliminado exitosamente', 'success')
    except APIError as e:
        flash(f'Error al eliminar el producto: {e.message}', 'danger')
        
    return redirect(url_for('productos.index'))
