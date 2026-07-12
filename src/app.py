# from flask import Flask, render_template

# app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(debug=True)

from src import crate_app

app = crate_app('development')

if __name__ == '__main__':
    print(' Frontend corriemdo en http://localhost:5001')
    app.run(debug=True, port=5001)


#* Ahora las rutas seran gestionadas por los archivos controller

'''@app.route("/")
def index():
    return render_template("index.html", nombre_usuario = "Marlon Quintero")

#! Rutas Clientes

@app.route("/nuevo-cliente")
def nuevoCliente():
    return render_template("clientes/NuevoCliente.html")

@app.route("/ver-clientes")
def listaClientes():
    return render_template("clientes/VerClientes.html")


#! Rutas Productos

@app.route("/nuevo-producto")
def nuevoproducto():
    return render_template("productos/NuevoProducto.html")

@app.route("/ver-producto")
def verproducto():
    return render_template("productos/VerProducto.html")

#! Rutas Facturas

@app.route("/nueva-factura")
def nuevafactura():
    return render_template("facturas/NuevaFactura.html")

@app.route("/ver-factura")
def verfactura():
    return render_template("facturas/VerFactura.html")

'''