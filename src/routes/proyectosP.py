from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.utils.db import db

proyectosP = Blueprint('proyectosP', __name__)

@proyectosP.route('/lista-proyectos')
def vistaListaProyectos():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logoutUser'))
    asociaciones = usuario.proyectos_asociados
    return render_template('vistas_participantes/listaProyectos.html', usuario=usuario, asociaciones=asociaciones)

@proyectosP.route('/acceder-proyectoP/<string:idProyecto>')
def accederProyectoP(idProyecto):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logoutUser'))
    session['proyecto_id'] = idProyecto
    return redirect(url_for('accionesP.vistaListaAccionesP'))

@proyectosP.route('/regresar-proyectosP')
def regresarProyectosP():
    session.pop('proyecto_id')
    return redirect(url_for('proyectosP.vistaListaProyectos'))