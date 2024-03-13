from src.utils.db import db
from uuid import uuid4

def getDefaultID() -> str:
    return uuid4().hex

class Activo(db.Model):
    __tablename__ = 'Activos'
    idActivo = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    clave = db.Column(db.String(15), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    propietario = db.Column(db.String(30), nullable=False)
    ubicacion = db.Column(db.String(30), nullable=False)
    frecMantenimiento = db.Column(db.String(20), nullable=True)
    frecRenovacion = db.Column(db.String(20), nullable=True)
    fechaAdquisicion = db.Column(db.Date, nullable=False)
    tipoActivo = db.Column(db.String(20), nullable=False)
    confidencialidad = db.Column(db.Integer, nullable=False)
    disponibilidad = db.Column(db.Integer, nullable=False)
    integridad = db.Column(db.Integer, nullable=False)
    sensibilidad = db.Column(db.Integer, nullable=False)
    idProyecto = db.Column(db.String(32), db.ForeignKey('Proyectos.idProyecto', ondelete='CASCADE'), nullable=False)

    def __init__(self, clave, nombre, descripcion, propietario, ubicacion, frecMantenimiento, frecRenovacion, fechaAdquisicion, tipoActivo, idProyecto) -> None:
        self.clave = clave
        self.nombre = nombre
        self.descripcion = descripcion
        self.propietario = propietario
        self.ubicacion = ubicacion
        self.frecMantenimiento = frecMantenimiento
        self.frecRenovacion = frecRenovacion
        self.fechaAdquisicion = fechaAdquisicion
        self.tipoActivo = tipoActivo
        self.confidencialidad = 0
        self.disponibilidad = 0
        self.integridad = 0
        self.sensibilidad = 0
        self.idProyecto = idProyecto

    def evaluarActivo(self, confidencialidad, disponibilidad, integridad) -> None:
        self.confidencialidad = confidencialidad
        self.disponibilidad = disponibilidad
        self.integridad = integridad
        self.sensibilidad = self.confidencialidad + self.disponibilidad + self.integridad