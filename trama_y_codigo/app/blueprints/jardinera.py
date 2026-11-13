"""
Blueprint: La Jardinera — Panel de Administración.
Solo la guardiana del jardín puede plantar, podar y cuidar el ecosistema.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, login_manager
from app.models.usuario import Usuario

bp = Blueprint('jardinera', __name__, template_folder='../templates/jardinera')


@bp.before_request
def solo_la_jardinera():
    """Todo el panel, incluido el CRUD, es solo para la jardinera."""
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.es_jardinera:
        flash('Solo la jardinera puede acceder a este rincón.', 'error')
        return redirect(url_for('jardin.escena'))

@bp.route('/jardinera')
@login_required
def dashboard():
    """Panel de la jardinera — Vista general del ecosistema."""
    if not current_user.es_jardinera:
        flash('Solo la jardinera puede acceder a este rincón.', 'error')
        return redirect(url_for('jardin.escena'))

    from app.models import (
        ProyectoSoftware, ProyectoFibras,
        EntradaBitacora, ProductoBosque, ConexionMicelio
    )
    from app.models.canasto import Pedido
    stats = {
        'flores': ProyectoSoftware.query.count(),
        'tramas': ProyectoFibras.query.count(),
        'entradas': EntradaBitacora.query.count(),
        'tesoros': ProductoBosque.query.count(),
        'conexiones': ConexionMicelio.query.count(),
        'pedidos': Pedido.query.filter_by(estado_pago='pendiente').count()
    }
    return render_template('jardinera/dashboard.html', stats=stats)


@bp.route('/jardinera/pedidos')
@login_required
def pedidos():
    """Revisar los intercambios del bosque."""
    if not current_user.es_jardinera:
        return redirect(url_for('jardin.escena'))

    from app.models.canasto import Pedido
    lista_pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('jardinera/pedidos.html', pedidos=lista_pedidos)


@bp.route('/jardinera/pedidos/<int:pedido_id>/aprobar', methods=['POST'])
@login_required
def aprobar_pedido(pedido_id):
    """Marca un pedido manual (Nequi) como completado tras verificar el pago."""
    if not current_user.es_jardinera:
        return redirect(url_for('jardin.escena'))
    
    from app.models.canasto import Pedido
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado_pago = 'completado'
    db.session.commit()
    flash(f'El pedido #{pedido.id} ha florecido exitosamente.', 'exito')
    return redirect(url_for('jardinera.pedidos'))


# ═══════════════════════════════════════════════════
# RUTAS CRUD — Gestión Autónoma del Ecosistema
# ═══════════════════════════════════════════════════

from app.forms import FlorForm, TramaForm, BitacoraForm, TesoroForm
from app.services.almacen import guardar_archivo

def guardar_imagen(file_obj, prefijo):
    """Guarda una imagen en el álbum y retorna lo que debe ir a la base."""
    return guardar_archivo(file_obj, 'imagenes', prefijo)

# ── CRUD: FLORES (Software) ──
@bp.route('/jardinera/flores')
@login_required
def flores_index():
    from app.models.semillero import ProyectoSoftware
    items = ProyectoSoftware.query.order_by(ProyectoSoftware.fecha_brote.desc()).all()
    config = {
        'titulo': 'Semillero (Software)',
        'entidad': 'flores',
        'columnas': [('ID', 'id'), ('Título', 'titulo'), ('Stack', 'stack_tecnico')]
    }
    return render_template('jardinera/crud_lista.html', items=items, config=config)

@bp.route('/jardinera/flores/crear', methods=['GET', 'POST'])
@login_required
def flores_crear():
    from app.models.semillero import ProyectoSoftware
    form = FlorForm()
    if form.validate_on_submit():
        img_filename = guardar_imagen(form.imagen.data, 'flor')
        flor = ProyectoSoftware(
            nombre_flor=form.nombre_flor.data,
            titulo=form.titulo.data,
            stack_tecnico=form.stack_tecnico.data,
            descripcion_logica=form.descripcion_logica.data,
            repo_url=form.repo_url.data,
            imagen_url=img_filename
        )
        db.session.add(flor)
        db.session.commit()
        flash('Nueva flor plantada en el semillero.', 'exito')
        return redirect(url_for('jardinera.flores_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo='Plantar nueva flor', volver_url=url_for('jardinera.flores_index'))

@bp.route('/jardinera/flores/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def flores_editar(id):
    from app.models.semillero import ProyectoSoftware
    flor = ProyectoSoftware.query.get_or_404(id)
    form = FlorForm(obj=flor)
    if form.validate_on_submit():
        flor.nombre_flor = form.nombre_flor.data
        flor.titulo = form.titulo.data
        flor.stack_tecnico = form.stack_tecnico.data
        flor.descripcion_logica = form.descripcion_logica.data
        flor.repo_url = form.repo_url.data
        
        img = guardar_imagen(form.imagen.data, 'flor')
        if img:
            flor.imagen_url = img
            
        db.session.commit()
        flash('La flor ha sido podada y actualizada.', 'exito')
        return redirect(url_for('jardinera.flores_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo=f'Editar: {flor.titulo}', volver_url=url_for('jardinera.flores_index'), imagen_actual=flor.imagen_url)

@bp.route('/jardinera/flores/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def flores_eliminar(id):
    from app.models.semillero import ProyectoSoftware
    flor = ProyectoSoftware.query.get_or_404(id)
    db.session.delete(flor)
    db.session.commit()
    flash('Flor removida del jardín.', 'info')
    return redirect(url_for('jardinera.flores_index'))

# ── CRUD: TRAMAS (Fibras) ──
@bp.route('/jardinera/tramas')
@login_required
def tramas_index():
    from app.models.tramas import ProyectoFibras
    items = ProyectoFibras.query.all()
    config = {
        'titulo': 'Tramas (Fibras)',
        'entidad': 'tramas',
        'columnas': [('ID', 'id'), ('Pieza', 'titulo_pieza'), ('Técnica', 'tecnica_tejido')]
    }
    return render_template('jardinera/crud_lista.html', items=items, config=config)

@bp.route('/jardinera/tramas/crear', methods=['GET', 'POST'])
@login_required
def tramas_crear():
    from app.models.tramas import ProyectoFibras
    form = TramaForm()
    if form.validate_on_submit():
        img_filename = guardar_imagen(form.imagen.data, 'trama')
        trama = ProyectoFibras(
            titulo_pieza=form.titulo_pieza.data,
            material=form.material.data,
            tecnica_tejido=form.tecnica_tejido.data,
            historia_trama=form.historia_trama.data,
            imagen_url=img_filename
        )
        db.session.add(trama)
        db.session.commit()
        flash('Nueva trama tejida en el portafolio.', 'exito')
        return redirect(url_for('jardinera.tramas_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo='Tejer nueva trama', volver_url=url_for('jardinera.tramas_index'))

@bp.route('/jardinera/tramas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def tramas_editar(id):
    from app.models.tramas import ProyectoFibras
    trama = ProyectoFibras.query.get_or_404(id)
    form = TramaForm(obj=trama)
    if form.validate_on_submit():
        trama.titulo_pieza = form.titulo_pieza.data
        trama.material = form.material.data
        trama.tecnica_tejido = form.tecnica_tejido.data
        trama.historia_trama = form.historia_trama.data
        
        img = guardar_imagen(form.imagen.data, 'trama')
        if img:
            trama.imagen_url = img
            
        db.session.commit()
        flash('La trama ha sido actualizada.', 'exito')
        return redirect(url_for('jardinera.tramas_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo=f'Editar: {trama.titulo_pieza}', volver_url=url_for('jardinera.tramas_index'), imagen_actual=trama.imagen_url)

@bp.route('/jardinera/tramas/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def tramas_eliminar(id):
    from app.models.tramas import ProyectoFibras
    trama = ProyectoFibras.query.get_or_404(id)
    db.session.delete(trama)
    db.session.commit()
    flash('Trama deshecha.', 'info')
    return redirect(url_for('jardinera.tramas_index'))

# ── CRUD: BITÁCORA (Refugio) ──
@bp.route('/jardinera/bitacora')
@login_required
def bitacora_index():
    from app.models.refugio import EntradaBitacora
    items = EntradaBitacora.query.order_by(EntradaBitacora.fecha_publicacion.desc()).all()
    config = {
        'titulo': 'Entradas de Bitácora (Refugio)',
        'entidad': 'bitacora',
        'columnas': [('ID', 'id'), ('Título', 'titulo_entrada'), ('Fecha', 'fecha_publicacion')]
    }
    return render_template('jardinera/crud_lista.html', items=items, config=config)

@bp.route('/jardinera/bitacora/crear', methods=['GET', 'POST'])
@login_required
def bitacora_crear():
    from app.models.refugio import EntradaBitacora
    form = BitacoraForm()
    if form.validate_on_submit():
        img_filename = guardar_imagen(form.imagen.data, 'bitacora')
        entrada = EntradaBitacora(
            titulo_entrada=form.titulo_entrada.data,
            humor_del_dia=form.humor_del_dia.data,
            contenido_calido=form.contenido_calido.data,
            imagen_url=img_filename
        )
        db.session.add(entrada)
        db.session.commit()
        flash('Nueva reflexión añadida al refugio.', 'exito')
        return redirect(url_for('jardinera.bitacora_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo='Escribir en la bitácora', volver_url=url_for('jardinera.bitacora_index'))

@bp.route('/jardinera/bitacora/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def bitacora_editar(id):
    from app.models.refugio import EntradaBitacora
    entrada = EntradaBitacora.query.get_or_404(id)
    form = BitacoraForm(obj=entrada)
    if form.validate_on_submit():
        entrada.titulo_entrada = form.titulo_entrada.data
        entrada.humor_del_dia = form.humor_del_dia.data
        entrada.contenido_calido = form.contenido_calido.data
        
        img = guardar_imagen(form.imagen.data, 'bitacora')
        if img:
            entrada.imagen_url = img
            
        db.session.commit()
        flash('Reflexión actualizada.', 'exito')
        return redirect(url_for('jardinera.bitacora_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo=f'Editar: {entrada.titulo_entrada}', volver_url=url_for('jardinera.bitacora_index'), imagen_actual=entrada.imagen_url)

@bp.route('/jardinera/bitacora/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def bitacora_eliminar(id):
    from app.models.refugio import EntradaBitacora
    entrada = EntradaBitacora.query.get_or_404(id)
    db.session.delete(entrada)
    db.session.commit()
    flash('Entrada eliminada de la bitácora.', 'info')
    return redirect(url_for('jardinera.bitacora_index'))

# ── CRUD: TESOROS (Bosque) ──
@bp.route('/jardinera/tesoros')
@login_required
def tesoros_index():
    from app.models.bosque import ProductoBosque
    items = ProductoBosque.query.all()
    config = {
        'titulo': 'Inventario del Bosque (Tienda)',
        'entidad': 'tesoros',
        'columnas': [('ID', 'id'), ('Tesoro', 'producto'), ('Precio', 'precio'), ('Stock', 'stock_disponible')]
    }
    return render_template('jardinera/crud_lista.html', items=items, config=config)

@bp.route('/jardinera/tesoros/crear', methods=['GET', 'POST'])
@login_required
def tesoros_crear():
    from app.models.bosque import ProductoBosque
    form = TesoroForm()
    if form.validate_on_submit():
        img_filename = guardar_imagen(form.imagen.data, 'tesoro')
        tesoro = ProductoBosque(
            producto=form.producto.data,
            precio=form.precio.data,
            categoria=form.categoria.data,
            stock_disponible=form.stock_disponible.data,
            descripcion=form.descripcion.data,
            imagen_url=img_filename
        )
        db.session.add(tesoro)
        db.session.commit()
        flash('Nuevo tesoro plantado en el bosque.', 'exito')
        return redirect(url_for('jardinera.tesoros_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo='Añadir nuevo tesoro', volver_url=url_for('jardinera.tesoros_index'))

@bp.route('/jardinera/tesoros/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def tesoros_editar(id):
    from app.models.bosque import ProductoBosque
    tesoro = ProductoBosque.query.get_or_404(id)
    form = TesoroForm(obj=tesoro)
    if form.validate_on_submit():
        tesoro.producto = form.producto.data
        tesoro.precio = form.precio.data
        tesoro.categoria = form.categoria.data
        tesoro.stock_disponible = form.stock_disponible.data
        tesoro.descripcion = form.descripcion.data
        
        img = guardar_imagen(form.imagen.data, 'tesoro')
        if img:
            tesoro.imagen_url = img
            
        db.session.commit()
        flash('El tesoro ha sido actualizado.', 'exito')
        return redirect(url_for('jardinera.tesoros_index'))
    return render_template('jardinera/crud_form.html', form=form, titulo=f'Editar: {tesoro.producto}', volver_url=url_for('jardinera.tesoros_index'), imagen_actual=tesoro.imagen_url)

@bp.route('/jardinera/tesoros/<int:id>/eliminar', methods=['GET', 'POST'])
@login_required
def tesoros_eliminar(id):
    from app.models.bosque import ProductoBosque
    tesoro = ProductoBosque.query.get_or_404(id)
    db.session.delete(tesoro)
    db.session.commit()
    flash('Tesoro removido del bosque.', 'info')
    return redirect(url_for('jardinera.tesoros_index'))

