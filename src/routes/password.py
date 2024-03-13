from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.utils.crypto import bcrypt
from src.utils.db import db

password = Blueprint('password', __name__)

@password.route('/change-password')
def vistaConfirmarContraseña():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    return render_template('password/confirmarPassword.html')

@password.route('/new-password')
def vistaCambiarContraseña():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    return render_template('password/cambiarPassword.html')

@password.route('/check-password', methods=['POST'])
def verificarContraseña():
    if request.method == 'POST':
        password = request.form['password']
        usuario = Usuario.query.filter_by(idUsuario=session['user_id']).first()
        if not usuario.verificarContrasena(password):
            flash('danger')
            flash('Contraseña incorrecta')
            if usuario.rol == 1:
                return redirect(url_for('proyectosP.vistaListaProyectos'))
            else:
                if 'proyecto_id' in session:
                    return redirect(url_for('home.vistaHome'))
                else:
                    return redirect(url_for('proyectos.vistaListaProyectos'))
        return redirect(url_for('password.vistaCambiarContraseña')) 

@password.route('/update-password', methods=['POST'])
def actualizarContraseña():
    if request.method == 'POST':
        password = request.form['password-new']
        new_password = request.form['new-password']
        usuario = Usuario.query.filter_by(idUsuario=session['user_id']).first()
        if password == new_password:
            usuario.contrasena = bcrypt.generate_password_hash(new_password)
            db.session.commit()
            flash('success')
            flash('Su contraseña fue actualizada correctamente')
            return redirect(url_for('login.logoutUser'))
        else:
            flash('danger')
            flash('Error: Las contraseñas no coinciden. Por favor, inténtelo de nuevo.')
            return redirect(url_for('password.vistaCambiarContraseña')) 
