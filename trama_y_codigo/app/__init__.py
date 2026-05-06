"""
Trama & Código — Application Factory.

Aquí nace el ecosistema. Como una semilla que al recibir agua y luz
se convierte en un jardín completo, esta función crea la aplicación
con todas sus raíces, tallos y flores.

"Diseño y programo como si mi alma fuera requerida para crear mis aplicaciones"
"""
from flask import Flask
from app.config import configuraciones
from app.extensions import db, login_manager, csrf
from app.services.reloj_logico import obtener_estado_mundo
from datetime import datetime
from sqlalchemy import text
import os, sys, logging


def create_app(entorno='default'):
    """
    Factory Pattern — Planta una nueva instancia del jardín.

    Args:
        entorno: 'desarrollo', 'produccion' o 'default'

    Returns:
        Flask app: El jardín listo para florecer.
    """
    app = Flask(__name__)

    # ── Configuración ──
    app.config.from_object(configuraciones[entorno])

    # ── Inicializar extensiones (las raíces) ──
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── Registrar Blueprints (los movimientos del paisaje) ──
    from app.blueprints.jardin import bp as jardin_bp
    from app.blueprints.refugio import bp as refugio_bp
    from app.blueprints.semillero import bp as semillero_bp
    from app.blueprints.tramas import bp as tramas_bp
    from app.blueprints.bosque import bp as bosque_bp
    from app.blueprints.micelio import bp as micelio_bp
    from app.blueprints.retrato import bp as retrato_bp
    from app.blueprints.canasto import bp as canasto_bp
    from app.blueprints.jardinera import bp as jardinera_bp

    from app.blueprints import jardin, refugio, semillero, tramas, bosque, micelio, retrato, canasto, jardinera, auth, debug

    app.register_blueprint(debug.bp)
    app.register_blueprint(jardin_bp)
    app.register_blueprint(refugio_bp)
    app.register_blueprint(semillero_bp)
    app.register_blueprint(tramas_bp)
    app.register_blueprint(bosque_bp)
    app.register_blueprint(micelio_bp)
    app.register_blueprint(retrato_bp)
    app.register_blueprint(canasto_bp)
    app.register_blueprint(jardinera_bp)
    app.register_blueprint(auth.bp)

    # ── Context Processor: Inyectar el estado del mundo en todas las plantillas ──
    @app.context_processor
    def inyectar_estado_mundo():
        """El reloj lógico está disponible en cada rincón del jardín."""
        return {
            'estado_mundo': obtener_estado_mundo(),
        }

    # ── Crear tablas de la base de datos ──
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()
        _sembrar_datos_iniciales(app)

    def get_log_path():
        if os.name == 'nt': # Windows local
            return os.path.join(app.root_path, 'error_log.txt')
        return '/tmp/error_log.txt' # Linux/Render

    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        error_info = traceback.format_exc()
        logging.error(f"!!! ERROR 500 !!!\n{error_info}")
        try:
            with open(get_log_path(), 'a') as f:
                f.write(f"\n--- ERROR 500 at {datetime.now()} ---\n")
                f.write(error_info)
        except:
            pass
        return "Error Interno del Servidor. Se ha registrado el detalle en el log del servidor.", 500

    return app


def _sembrar_datos_iniciales(app):
    """
    Siembra datos de ejemplo si el jardín está vacío.
    Solo se ejecuta la primera vez.
    """
    from app.models.usuario import Usuario
    from app.models.semillero import ProyectoSoftware
    from app.models.tramas import ProyectoFibras
    from app.models.refugio import EntradaBitacora
    from app.models.bosque import ProductoBosque

    # ── Asegurar la existencia de la Jardinera (admin) ──
    jardinera = Usuario.query.filter_by(rol='administradora').first()
    if not jardinera:
        jardinera = Usuario(
            username='LindaChocolatina',
            email='lindasioc@gmail.com',
            rol='administradora'
        )
        jardinera.plantar_contrasena('Juanita1509:)')
        db.session.add(jardinera)
        db.session.commit()
        print('[OK] Jardinera creada exitosamente.')
    else:
        # Forzar actualización por si se cambió algo en el código
        jardinera.username = 'LindaChocolatina'
        jardinera.email = 'lindasioc@gmail.com'
        jardinera.plantar_contrasena('Juanita1509:)')
        db.session.commit()
        print('[OK] Credenciales de Jardinera actualizadas.')
    
    # Si ya hay otros datos, no sembrar el resto
    if ProyectoSoftware.query.first():
        return

    # ── Sembrar flores en el Semillero ──
    flores = [
        ProyectoSoftware(
            nombre_flor='Lupino Azul',
            titulo='Trama & Código',
            stack_tecnico='Python, Flask, SQLite, JavaScript',
            descripcion_logica='Un ecosistema digital que es portafolio, blog y tienda. El código respira al ritmo del tiempo.',
            repo_url='https://github.com/tramaycodigo'
        ),
        ProyectoSoftware(
            nombre_flor='Diente de León',
            titulo='API de Semillas',
            stack_tecnico='Python, Flask, PostgreSQL',
            descripcion_logica='Una API RESTful que distribuye semillas de conocimiento técnico a quien las necesite.',
        ),
        ProyectoSoftware(
            nombre_flor='Trébol Silvestre',
            titulo='Gestor de Invernadero',
            stack_tecnico='Java, Spring Boot, MySQL',
            descripcion_logica='Sistema de gestión para invernaderos urbanos con monitoreo de humedad y temperatura.',
        ),
    ]
    db.session.add_all(flores)

    # ── Tejer Tramas ──
    tramas = [
        ProyectoFibras(
            material='Lana merino',
            tecnica_tejido='Crochet amigurumi',
            titulo_pieza='El Bosque Miniatura',
            historia_trama='Un conjunto de pinos, hongos y animales tejidos a mano que replican el ecosistema del jardín en miniatura.',
        ),
        ProyectoFibras(
            material='Algodón orgánico',
            tecnica_tejido='Macramé',
            titulo_pieza='Red de Micelio',
            historia_trama='Un tapiz de macramé que simboliza las conexiones invisibles entre personas y proyectos.',
        ),
    ]
    db.session.add_all(tramas)

    # ── Escribir en la Bitácora ──
    entradas = [
        EntradaBitacora(
            titulo_entrada='El día que el código aprendió a respirar',
            contenido_calido='Hoy implementé el reloj lógico. El jardín ahora cambia con las horas del día, como si el código mismo pudiera sentir el paso del tiempo. La madrugada trae niebla, el mediodía trae sol, y la noche trae luciérnagas. No es solo un sitio web — es un organismo vivo.',
            humor_del_dia='Inspirada',
        ),
        EntradaBitacora(
            titulo_entrada='Tejer y programar: la misma paciencia',
            contenido_calido='Ayer terminé un amigurumi mientras esperaba que el deploy terminara. Me di cuenta de que tejer y programar requieren la misma virtud: paciencia. Cada puntada es una línea de código, cada fila es una función. Al final, ambos crean algo que antes no existía.',
            humor_del_dia='Reflexiva',
        ),
    ]
    db.session.add_all(entradas)

    # ── Plantar tesoros en el Bosque ──
    tesoros = [
        ProductoBosque(
            producto='Amigurumi: Amanita Muscaria',
            precio=45000,
            categoria='fisico',
            stock_disponible=5,
            descripcion='Hongo tejido a mano en crochet con lana merino. Cada pieza es única.'
        ),
        ProductoBosque(
            producto='Plantilla Flask: Jardín Starter',
            precio=25000,
            categoria='digital',
            stock_disponible=999,
            descripcion='Plantilla de Flask con estructura de proyecto lista para florecer.'
        ),
        ProductoBosque(
            producto='Set de Stickers: Botánica Digital',
            precio=12000,
            categoria='fisico',
            stock_disponible=20,
            descripcion='Set de 10 stickers ilustrados con flores y código entrelazados.'
        ),
    ]
    db.session.add_all(tesoros)

    db.session.commit()
    print('[OK] El jardin ha sido sembrado con datos iniciales.')
