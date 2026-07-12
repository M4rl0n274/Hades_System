#se encarga de iniciar la aplicación y de impórtar las rutas

from flask import Flask, session

def crate_app(config_name='default'):
    app = Flask(__name__)
    from src.config.config import config
    app.config.from_object(config[config_name])
    
    #importar la ruta de clientes
    from src.controllers.clientes_controller  import cliente_bp
    from src.controllers.home_controller      import home_bp
    
    app.register_blueprint(cliente_bp,   url_prefix='/clientes')
    app.register_blueprint(home_bp,      url_prefix='/')
    
    return app
    
    
    