from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.responsables import Participantes
from src.utils.db import db

proyectos = Blueprint('proyectos', __name__)

@proyectos.route('/proyectos')
def vistaListaProyectos():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logoutUser'))
    proyectos = []
    for asociaciones in usuario.proyectos_asociados:
        proyectos.append(asociaciones.proyecto)
    return render_template('proyectos/listaProyectos.html', usuario=usuario, proyectos=proyectos)

@proyectos.route('/editar-proyecto/<string:idProyecto>')
def vistaEditarProyecto(idProyecto):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    proyecto = Proyecto.query.filter_by(idProyecto=idProyecto).first()
    return render_template('proyectos/editarProyecto.html', usuario=usuario, proyecto=proyecto)

@proyectos.route('/anadir-proyecto', methods=['POST'])
def añadirProyecto():
    if request.method == 'POST':
        try:
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            p = Proyecto(clave=clave,nombre=nombre, descripcion=descripcion)
            db.session.add(p)
            proyecto = Proyecto.query.filter_by(clave=clave).first()
            usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
            asociacion = Participantes(usuario=usuario, proyecto=proyecto, estado='Dueño')
            db.session.add(asociacion)
            db.session.commit()
            flash('success')
            flash('Proyecto creado correctamente')
        except:
            db.session.rollback()
            flash('danger')
            flash('La clave del proyecto ya existe')
        return redirect(url_for('proyectos.vistaListaProyectos'))

@proyectos.route('/modificar-proyecto', methods=['POST'])
def modificarProyecto():
    if request.method == 'POST':
        try:
            idProyecto = request.form['idproyecto']
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            p = Proyecto.query.filter_by(idProyecto=idProyecto).first()
            p.clave = clave
            p.nombre = nombre
            p.descripcion = descripcion
            db.session.commit()
            flash('success')
            flash('Proyecto modificado correctamente')
        except:
            db.session.rollback()
            flash('danger')
            flash('La clave del proyecto ya existe')
        return redirect(url_for('proyectos.vistaListaProyectos'))

@proyectos.route('/seleccionar-proyecto/<string:idProyecto>')
def seleccionarProyecto(idProyecto):
    session['proyecto_id'] = idProyecto
    return redirect(url_for('home.vistaHome'))