from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto

planes = Blueprint('planes', __name__)

@planes.route('/listar-planes')
def vistaListaPlanes():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logoutUser'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    #responsables = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    return render_template('planes/listaPlanes.html', usuario=usuario, proyecto=proyecto)


@planes.route('/listar-planes-usuario')
def vistaListaPlanesUsuario():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logoutUser'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    #responsables = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    return render_template('planes/listaPlanesUsuario.html', usuario=usuario, proyecto=proyecto)