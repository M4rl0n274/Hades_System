from flask import Blueprint, render_template, session, redirect, url_for
from src.clients.api_client import APIClient, APIError
from src.controllers.auth_controller import login_required

home_bp = Blueprint('home', __name__)


def _client():
    return APIClient(session.get('api_token'))


@home_bp.route('/')
@login_required
def index():
    usuario = session.get('usuario', {})
    rol = usuario.get('rol')

    # El rol Usuario no accede al Dashboard, va directo a Productos
    if rol == 'Usuario':
        return redirect(url_for('productos.index'))

    # Métricas base para el Dashboard
    kpis = {
        'total_productos': 0,
        'total_clientes': 0,
        'total_facturas': 0,
        'ingresos_totales': 0
    }

    grafica_data = {
        'labels': [],
        'valores': []
    }

    try:
        # 1. Cargar Total de Productos
        res_prod = _client().get('/productos/', params={'per_page': 1})
        if isinstance(res_prod, dict):
            kpis['total_productos'] = res_prod.get('meta', {}).get('total', 0)

        # 2. Cargar Total de Clientes
        res_cli = _client().get('/clientes/', params={'per_page': 1})
        if isinstance(res_cli, dict):
            kpis['total_clientes'] = res_cli.get('meta', {}).get('total', 0)

        # 3. Datos exclusivos para el Administrador
        if rol == 'Administrador':
            res_fact = _client().get('/factura/', params={'per_page': 50})
            if isinstance(res_fact, dict):
                facturas = res_fact.get('data', [])
                kpis['total_facturas'] = res_fact.get('meta', {}).get('total', len(facturas))

                # Sumatoria de ingresos totales
                kpis['ingresos_totales'] = sum(float(f.get('total', 0)) for f in facturas)

                # Prepara datos para la gráfica (últimas facturas emitidas)
                ultimas = list(reversed(facturas[:7]))
                grafica_data['labels'] = [f"Factura #{f.get('id')}" for f in ultimas]
                grafica_data['valores'] = [float(f.get('total', 0)) for f in ultimas]

    except Exception:
        pass

    return render_template('home/index.html', usuario=usuario, kpis=kpis, grafica_data=grafica_data)