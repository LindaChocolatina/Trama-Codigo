"""
Trama & Código — Punto de entrada.
Aquí comienza todo: la semilla germina.

"La normalidad nunca ha creado magia"
"""
from app import create_app

import os

def _detectar_entorno():
    """
    Detecta el entorno de ejecución.
    - Render/Producción: APP_ENV=produccion  (o FLASK_ENV=production como fallback)
    - Local/Desarrollo:  sin variable (default)
    """
    env = os.environ.get('APP_ENV') or os.environ.get('FLASK_ENV', 'desarrollo')
    # Render suele poner FLASK_ENV=production (inglés) — mapeamos al nombre interno
    if env == 'production':
        env = 'produccion'
    return env

app = create_app(_detectar_entorno())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
