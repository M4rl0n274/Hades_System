from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required, rol_required

factura_bp = Blueprint('facturas', __name__)


def _client():
    return APIClient(session.get('api_token'))

@factura_bp.route('/')
@login_required
@rol_required('Administrador')
def index():
    q = request.args.get('q', '').strip()
    try:
        data = _client().get('/factura/')
        facturas = APIClient.as_list(data)
    except APIError as e:        
        facturas = []
        
    return render_template('facturas/VerFacturas.html', facturas=facturas, q=q)

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

    return render_template('facturas/FormFacturas.html')