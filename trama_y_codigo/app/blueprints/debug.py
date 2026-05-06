"""
Blueprint: Debug — Diagnóstico del Ecosistema.
Herramientas de monitoreo para la jardinera técnica.
"""
from flask import Blueprint, current_app, jsonify
from app.extensions import db
from sqlalchemy import text
import os, sys, datetime

bp = Blueprint('debug', __name__)


def get_log_path():
    if os.name == 'nt':
        return os.path.join(current_app.root_path, 'error_log.txt')
    return '/tmp/error_log.txt'


@bp.route('/health')
def health():
    """
    Endpoint de salud — Para monitores de uptime (UptimeRobot, etc.).
    Hace un ping real a la DB para mantener activos Render y Supabase.
    """
    db_ok = False
    try:
        db.session.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        pass

    status = 'ok' if db_ok else 'degraded'
    code = 200 if db_ok else 503
    return jsonify({
        'status': status,
        'db': 'conectada' if db_ok else 'error',
        'ts': datetime.datetime.utcnow().isoformat()
    }), code


@bp.route('/debug-logs')
def debug_logs():
    db_status = "Desconocido"
    try:
        db.session.execute(text('SELECT 1'))
        db_status = "Conectada (OK)"
    except Exception as e:
        db_status = f"Error de Conexión: {str(e)}"

    logs = "No hay logs registrados todavía."
    log_path = get_log_path()
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            logs = f.read()

    admin_check = "No verificado"
    try:
        from app.models.usuario import Usuario
        admin = Usuario.query.filter_by(rol='administradora').first()
        if admin:
            admin_check = f"Encontrada: {admin.username} ({admin.email})"
        else:
            admin_check = "NO ENCONTRADA"
    except Exception as e:
        admin_check = f"Error al buscar admin: {str(e)}"

    env_info = f"Python {sys.version} | OS: {os.name} | Root: {current_app.root_path}"

    return f"""
    <html>
    <head><title>Diagnóstico T&C</title></head>
    <body style="font-family: monospace; padding: 20px;">
        <h1>🌿 Diagnóstico del Jardín</h1>
        <p><strong>Entorno:</strong> {env_info}</p>
        <p><strong>Estado de Base de Datos:</strong> {db_status}</p>
        <p><strong>Admin Check:</strong> {admin_check}</p>
        <p><strong>Ruta del Log:</strong> {log_path}</p>
        <hr>
        <h3>Logs de Error:</h3>
        <pre style="background: #f4f4f4; padding: 15px; border: 1px solid #ddd;">{logs}</pre>
        <br>
        <a href="/">Volver al Jardín</a>
    </body>
    </html>
    """
