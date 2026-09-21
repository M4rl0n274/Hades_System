from flask import Flask, render_template, session



from src import create_app

app = create_app('development')

if __name__ == '__main__':
    print('✓ Frontend corriendo en http://localhost:5001')
    app.run(debug=True, port=5001)
    
    
    
    
    
    
#* Filtro Personalizado de Jinja2 para Formato de Moneda (COP)
# ---------------------------------------------------------------------------
@app.template_filter('cop')
def format_cop(valor):
    """Formatea un número a pesos colombianos con 2 decimales y coma (ej: $1.000.000,00)."""
    try:
        val = float(valor)
        # Formato estándar con las comas para miles y puntos para decimales
        formatted = f"{val:,.2f}"
        # Intercambiamos separadores: comas -> puntos y puntos -> comas
        formatted = formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
        return f"${formatted}"
    except (ValueError, TypeError):
        return "$0,00"
    
    
# sirve para mostrsr o no dinamicamente el opciones del Navbar dependiendo del rol
@app.context_processor
def utility_processor():
    def tiene_rol(*roles):
        usuario = session.get('usuario') or {}
        return usuario.get('rol') in roles
    return dict(tiene_rol=tiene_rol)

# #! Rutas Clientes

# @app.route("/nuevo-cliente")
# def nuevoCliente():
#     return render_template("clientes/NuevoCliente.html")

# @app.route("/ver-clientes")
# def listaClientes():
#     return render_template("clientes/VerClientes.html")


# #! Rutas Productos

# @app.route("/nuevo-producto")
# def nuevoproducto():
#     return render_template("productos/NuevoProducto.html")

# @app.route("/ver-producto")
# def verproducto():
#     return render_template("productos/VerProducto.html")

# #! Rutas Facturas

# @app.route("/nueva-factura")
# def nuevafactura():
#     return render_template("facturas/NuevaFactura.html")

# @app.route("/ver-factura")
# def verfactura():
#     return render_template("facturas/VerFactura.html")
