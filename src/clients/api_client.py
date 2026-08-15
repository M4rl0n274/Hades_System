#permite crear conexiones con la api rest
import httpx
# sirve para tomar la información de las variables globales que se han creado
from flask import current_app


class APIError(Exception):
    def __init__(self, message, status_code=400, errors=None):
        self.message    = message
        self.status_code = status_code
        self.errors     = errors
        super().__init__(message)

# para construir la conexión con la API
class APIClient:
    def __init__(self, token: str = None):
        self.base_url = current_app.config['API_BASE_URL']
        self.headers  = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = f'Bearer {token}' 

    def _url(self, path: str) -> str:
        ful_url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        print(f"APIClient: {ful_url}")
        return ful_url
    

# para dar un tratamiento de validación a l ainformación que llega
    def _handle(self, response: httpx.Response):
        if not response.content:
            raise APIError('El servidor retornó una respuesta vacía', response.status_code)

        try:
            body = response.json()
        except Exception:
            raise APIError(
                f'Respuesta no es JSON válido (status {response.status_code}): '
                f'{response.text[:200]}',
                response.status_code
            )

        # El backend retorna una lista directamente → envolverla
        if isinstance(body, list):
            return body  # los controladores recibirán la lista tal cual

        if not isinstance(body, dict):
            raise APIError(
                f'Formato de respuesta inesperado: {type(body).__name__}',
                response.status_code
            )

        # Backend con wrapper { success, data } (estructura propia)
        if 'success' in body:
            if not body.get('success'):
                raise APIError(
                    body.get('message', 'Error desconocido'),
                    response.status_code,
                    body.get('errors'),
                )
            return body.get('data')

        # Backend externo con dict plano (sin wrapper)
        if response.status_code < 400:
            return body
        raise APIError(
            body.get('message') or body.get('error') or 'Error del servidor',
            response.status_code
        )

    #* definir Get en clientes
    def get(self, path, params=None):
        print(path)
        r = httpx.get(self._url(path), params=params, headers=self.headers, timeout=10)
        print (r.text)
        return self._handle(r)
    
    #* POST Get en clientes
    def post(self, path, json=None):
        r = httpx.post(self._url(path), json=json, headers=self.headers, timeout=10)
        return self._handle(r)

    #Convertir en lista un resultado de datos
    @staticmethod
    def as_list(data):
        """Normaliza respuesta a lista, sea directa o paginada."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get('items') or data.get('data') or data.get('results') or []
        return []
    