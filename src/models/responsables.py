from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto

class Participantes(db.Model):
    __tablename__ = 'Participantes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUsuario = db.Column(db.String(32), db.ForeignKey('Usuarios.idUsuario'))
    idProyecto = db.Column(db.String(32), db.ForeignKey('Proyectos.idProyecto'))
    usuario = db.relationship('Usuario', backref='proyectos_asociados')
    proyecto = db.relationship('Proyecto', backref='usuarios_asociados')
    estado = db.Column(db.String(10))