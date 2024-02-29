from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.utils.crypto import bcrypt
from src.utils.db import db

responsables = Blueprint('responsables', __name__)

@responsables.route('/edicion-responsable/<string:idResponsable>')
def vistaEdicionResponsables(idResponsable):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    responsable = Usuario.query.filter_by(idUsuario = idResponsable).first()
    return render_template('responsables/modificarResponsables.html', usuario=usuario, responsable=responsable)

@responsables.route('/anadir-responsable', methods=['POST'])
def añadirResponsable():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            aPaterno = request.form['aPaterno']
            aMaterno = request.form['aMaterno']
            email = request.form['email']
            telefono = request.form['tel']
            password = request.form['password']
            u = Usuario(
                nombre=nombre,
                apellidoPaterno=aPaterno,
                apelidoMaterno=aMaterno,
                correo=email,
                telefono=telefono,
                contrasena=bcrypt.generate_password_hash(password),
                rol=1,
                idJefe=session['user_id']
            )
            db.session.add(u)
            db.session.commit()
            flash('success')
            flash('El participante fue añadido correctamente')
        except:
            db.session.rollback()
            flash('danger')
            flash('El correo o télefono que ingreso ya existe en el sistema')
        return redirect(url_for('proyectos.vistaListaProyectos'))


@responsables.route('/actualizar-responsable', methods=['POST'])
def modificarResponsable():
    if request.method == 'POST':
        idResponsable = request.form['idResponsable']
        nombre = request.form['nombre']
        aPaterno = request.form['aPaterno']
        aMaterno = request.form['aMaterno']
        email = request.form['email']
        telefono = request.form['telefono']
        responsable = Usuario.query.filter_by(idUsuario=idResponsable).first()
        responsable.nombre = nombre
        responsable.apellidoPaterno = aPaterno
        responsable.apellidoMaterno = aMaterno
        responsable.correo = email
        responsable.telefono = telefono
        db.session.commit()
        flash('success')
        flash('El participante fue modificado correctamente')
        return redirect(url_for('proyectos.vistaListaProyectos'))