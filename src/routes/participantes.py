from flask import Blueprint, session, redirect, url_for, render_template, request, flash, Response, json
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.responsables import Participantes
from src.utils.db import db

participantes = Blueprint('participantes', __name__)

@participantes.route('/listar-participantes')
def vistaListaParticipantes():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    participantes_proyecto = []
    for asociacion in proyecto.usuarios_asociados:
        participantes_proyecto.append((asociacion.usuario, asociacion.estado, asociacion.id, asociacion.acciones))
    return render_template('participantes/listaParticipantes.html', usuario=usuario, participantes_proyecto=participantes_proyecto)

@participantes.route('/get_participantes', methods=['GET'])
def obtenerParticipantes():
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    participantes_jefe = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    participantes_proyecto = []
    for asociacion in proyecto.usuarios_asociados:
        participantes_proyecto.append((asociacion.usuario, asociacion.estado))
    participantes_listado = []
    for participante in participantes_jefe:
        if not participante in [x[0] for x in participantes_proyecto]:
            participantes_listado.append(participante.correo)
    return Response(json.dumps(participantes_listado), mimetype='application/json')

@participantes.route('/anadir-nuevo-participante', methods=['POST'])
def crearParticipante():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            aPaterno = request.form['aPaterno']
            aMaterno = request.form['aMaterno']
            email = request.form['email']
            telefono = request.form['tel']
            departamento = request.form['departamento']
            cargo = request.form['cargo']
            password = request.form['password']
            u = Usuario(
                nombre=nombre,
                apellidoPaterno=aPaterno,
                apelidoMaterno=aMaterno,
                correo=email,
                telefono=telefono,
                departamento=departamento,
                cargo=cargo,
                contrasena=password,
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
        return redirect(url_for('participantes.vistaListaParticipantes'))

@participantes.route('/anadir-participante', methods=['POST'])
def añadirParticipante():
    if request.method == 'POST':
        email = request.form['correo']
        participante = Usuario.query.filter_by(correo=email).first()
        if participante:
            proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
            asociacion = Participantes(usuario=participante, proyecto=proyecto, estado="Activo")
            db.session.add(asociacion)
            db.session.commit()
            flash("success")
            flash("El participante ha sido añadido al proyecto")
        else:
            flash("danger")
            flash("No existe un participante con el correo que ingresó")
        return redirect(url_for('participantes.vistaListaParticipantes'))

@participantes.route('/editar-estado-participante', methods=['POST'])
def editarEstadoParticipante():
    if request.method == 'POST':
        idParticipante = request.form['idParticipante']
        participante = Participantes.query.filter_by(id=idParticipante).first()
        estado = request.form['estado']
        if not participante.estado == estado:
            if estado == 'Suspendido':
                for accion in participante.acciones:
                    db.session.delete(accion)
                participante.estado = 'Suspendido'
            else:
                participante.estado = 'Activo'
            db.session.commit()
            flash("success")
            flash("El estado del participante ha sido cambiado correctamente")
        return redirect(url_for('participantes.vistaListaParticipantes'))


@participantes.route('/expulsar-participante/<string:idParticipante>')
def expulsarParticipante(idParticipante):
    participante = Usuario.query.filter_by(idUsuario = idParticipante).first()
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    asociacion = Participantes.query.filter_by(usuario = participante, proyecto=proyecto).first()
    db.session.delete(asociacion)
    db.session.commit()
    flash("success")
    flash("El participante ha sido expulsado del proyecto")
    return redirect(url_for('participantes.vistaListaParticipantes'))