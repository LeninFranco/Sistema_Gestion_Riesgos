from src.utils.db import db
from src.models.historialAcciones import HistorialAccion
from uuid import uuid4
from sqlalchemy import TEXT

def getDefaultID() -> str:
    return uuid4().hex

class Accion(db.Model):
    __tablename__ = 'Acciones'
    idAccion = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    clave = db.Column(db.String(255), nullable=False, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(TEXT, nullable=False)
    fechaIni = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date, nullable=False)
    objetivo = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    control = db.Column(db.String(255), nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(255), nullable=False)
    detalles = db.Column(TEXT, nullable=True)
    enTiempo = db.Column(db.Integer, nullable=True)
    fechaAviso = db.Column(db.Date, nullable=False)
    idParticipante = db.Column(db.Integer, db.ForeignKey('Participantes.id'))
    idRiesgo = db.Column(db.String(32), db.ForeignKey('Riesgos.idRiesgo'), nullable=False)
    historial = db.relationship('HistorialAccion', backref='accion', cascade='all, delete-orphan')

    def __init__(self, clave, nombre, descripcion, fechaIni, fechaFin, objetivo, categoria, control, porcentaje, estado,detalles, fechaAviso, idParticipante, idRiesgo) -> None:
        self.clave = clave
        self.nombre = nombre
        self.descripcion = descripcion
        self.fechaIni = fechaIni
        self.fechaFin = fechaFin
        self.objetivo = objetivo
        self.categoria = categoria
        self.control = control
        self.porcentaje = porcentaje
        self.estado = estado
        self.detalles = detalles
        self.enTiempo = 1
        self.fechaAviso = fechaAviso
        self.idParticipante = idParticipante
        self.idRiesgo = idRiesgo