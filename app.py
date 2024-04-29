from flask import Flask
from flask import render_template
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from src.utils.db import db
from src.utils.crypto import bcrypt
from src.routes.login import login
from src.routes.proyectos import proyectos
from src.routes.home import home
from src.routes.responsables import responsables
from src.routes.activos import activos
from src.routes.riesgos import riesgos
from src.routes.participantes import participantes
from src.routes.proyectosP import proyectosP
from src.routes.accionesP import accionesP
from src.routes.password import password
from src.routes.acciones import acciones
from src.models.acciones import Accion
from src.models.responsables import Participantes
from src.models.riesgo import Riesgo
from datetime import datetime
import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'src', 'database', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)

app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Cambia esto al servidor SMTP que estés utilizando
app.config['MAIL_PORT'] = 587  # Puerto del servidor SMTP (usualmente 587 para TLS)
app.config['MAIL_USE_TLS'] = True  # Usar TLS (True para la mayoría de los servidores)
app.config['MAIL_USERNAME'] = 'riskprotego.escom@outlook.com'  # Tu dirección de correo electrónico
app.config['MAIL_PASSWORD'] = 'riskprotegoTTA044'  # Tu contraseña de correo electrónico
app.config['MAIL_DEFAULT_SENDER'] = 'riskprotego.escom@outlook.com'  # Dirección predeterminada del remitente

app.register_blueprint(login)
app.register_blueprint(proyectos)
app.register_blueprint(home)
app.register_blueprint(responsables)
app.register_blueprint(activos)
app.register_blueprint(riesgos)
app.register_blueprint(participantes)
app.register_blueprint(proyectosP)
app.register_blueprint(accionesP)
app.register_blueprint(password)
app.register_blueprint(acciones)


db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

def enviar_correo():
    with app.app_context():
        acciones = Accion.query.filter_by(fechaAviso=datetime.today().date()).all()
        for accion in acciones:
            participante = Participantes.query.filter_by(id=accion.idParticipante).first()
            riesgo = Riesgo.query.filter_by(idRiesgo=accion.idRiesgo).first()
            usuario = participante.usuario
            proyecto = participante.proyecto
            msg_html = render_template('templateCorreo.html', accion=accion, proyecto=proyecto, riesgo=riesgo)
            msg = Message("Recordatorio: Tarea Pendiente", recipients=[usuario.correo])
            msg.html = msg_html
            mail.send(msg)

# Configurar el planificador de tareas
scheduler = BackgroundScheduler()
scheduler.add_job(enviar_correo, trigger='cron', hour=11, minute=18)  
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)