from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.responsables import Participantes
from src.models.acciones import Accion
from src.utils.db import db
from datetime import datetime

accionesP = Blueprint('accionesP', __name__)

@accionesP.route('/lista-accionesP')
def vistaListaAccionesP():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectosP.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    asociacion = Participantes.query.filter_by(idUsuario=usuario.idUsuario, idProyecto=proyecto.idProyecto).first()
    for accion in asociacion.acciones:
        accion.fechaFin = datetime.strptime(accion.fechaFin, '%Y-%m-%d')
    acciones_finalizadas_canceladas = []
    otras_acciones = []
    for accion in asociacion.acciones:
        if accion.estado in ['Finalizado', 'Cancelado']:
            acciones_finalizadas_canceladas.append(accion)
        else:
            otras_acciones.append(accion)
    otras_acciones_ordenadas = sorted(otras_acciones, key=lambda x: abs((datetime.now() - x.fechaFin).total_seconds()))
    acciones_ordenadas = otras_acciones_ordenadas + acciones_finalizadas_canceladas
    return render_template('vistas_participantes/listaAccionesP.html', usuario=usuario, proyecto=proyecto, acciones=acciones_ordenadas)

@accionesP.route('/modificar-estado-accion/<string:idAccion>')
def vistaModificacionEstadoAccion(idAccion):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectosP.vistaListaProyectos'))
    accion = Accion.query.filter_by(idAccion = idAccion).first()
    return render_template('vistas_participantes/editarEstado.html', usuario=usuario, accion=accion)

@accionesP.root_path('/actualizar-estado-accion', methods=['POST'])
def actualizarEstadoAccion():
    if request.method == 'POST':
        idAccion = request.form['idaccion']
        accion = Accion.query.filter_by(idAccion = idAccion).first()
        estado = request.form['estado']
        if estado == 'Iniciado':
            return redirect(url_for('accionesP.vistaListaAccionesP'))
        if estado == 'En Proceso':
            accion.porcentaje = float(request.form['porcentaje'])
        else:
            if estado == 'Finalizado':
                accion.porcentaje = 100.00
            accion.detalles = request.form['detalles']
        db.session.commit()
        flash('success')
        flash('El estado de la acción ha sido actualizada correctamente')
        return redirect(url_for('accionesP.vistaListaAccionesP'))
