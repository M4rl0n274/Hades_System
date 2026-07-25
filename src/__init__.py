from flask import Flask, session

def create_app(config_name='default'):
    app = Flask(__name__)
    from src.config.config import config
    app.config.from_object(config[config_name])

    #* Importar controller
    from src.controllers.clientes_controller  import cliente_bp
    from src.controllers.productos_controller  import producto_bp
    from src.controllers.home_controller      import home_bp
    #* registrar Ruta
    app.register_blueprint(producto_bp,   url_prefix='/productos')
    app.register_blueprint(cliente_bp,   url_prefix='/clientes')
    app.register_blueprint(home_bp,      url_prefix='/')

    return app