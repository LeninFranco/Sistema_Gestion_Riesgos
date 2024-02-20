from src.utils.db import db
from src.models.activos import Activo
from uuid import uuid4

def getDefaultID() -> str:
    return uuid4().hex

class Proyecto(db.Model):
    __tablename__ = "Proyectos"
    idProyecto = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    clave = db.Column(db.String(100), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    activos = db.relationship('Activo', backref='proyectoActivo', cascade='all, delete-orphan')
    usuarios = db.relationship('Usuario', secondary='Participantes', backref=db.backref('proyectos', lazy='dynamic'))

    def __init__(self, nombre, clave, descripcion) -> None:
        self.clave = clave
        self.nombre = nombre
        self.descripcion = descripcion