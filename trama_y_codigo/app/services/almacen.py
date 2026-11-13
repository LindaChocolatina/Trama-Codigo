"""
El Álbum — Dónde viven las imágenes del jardín.

Si existe CLOUDINARY_URL, las imágenes se guardan en Cloudinary y en la base
queda su URL completa. Si no, se guardan en static/uploads y en la base queda
solo el nombre del archivo.
"""
import os
from flask import current_app, url_for
from werkzeug.utils import secure_filename


def guardar_archivo(file_obj, carpeta, prefijo):
    """Guarda un archivo subido y retorna el valor que debe ir a la base de datos."""
    if not file_obj or file_obj.filename == '':
        return None

    if os.environ.get('CLOUDINARY_URL'):
        import cloudinary.uploader
        resultado = cloudinary.uploader.upload(
            file_obj,
            folder=f'trama_y_codigo/{carpeta}',
            resource_type='image',
        )
        return resultado['secure_url']

    filename = secure_filename(f"{prefijo}_{file_obj.filename}")
    ruta = os.path.join(current_app.root_path, 'static', 'uploads', carpeta)
    os.makedirs(ruta, exist_ok=True)
    file_obj.save(os.path.join(ruta, filename))
    return filename


def url_archivo(valor, carpeta):
    """Convierte lo guardado en la base en una URL que el navegador puede abrir."""
    if not valor:
        return ''
    if valor.startswith(('http://', 'https://')):
        return valor
    return url_for('static', filename=f'uploads/{carpeta}/{valor}')
