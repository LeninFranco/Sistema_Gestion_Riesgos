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
    return render_template('planes/listaPlanes.html', usuario=usuario)


@planes.route('/listar-planes-participante')
def vistaListaPlanesUsuario():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logoutUser'))
    return render_template('vistas_participantes/listaPlanesUsuario.html', usuario=usuario)