from src.utils.db import db
from datetime import datetime

def getFechaActual():
    return datetime.now().date()

class HistorialActivo(db.Model):
    __tablename__ = 'HistorialActivos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False, default=getFechaActual)
    confidencialidad = db.Column(db.Integer, nullable=False)
    disponibilidad = db.Column(db.Integer, nullable=False)
    integridad = db.Column(db.Integer, nullable=False)
    sensibilidad = db.Column(db.Integer, nullable=False)
    detalles = db.Column(db.String(255), nullable=False)
    idActivo = db.Column(db.String(32), db.ForeignKey('Activos.idActivo', ondelete='CASCADE'), nullable=False)

    def __init__(self, confidencialidad, disponibilidad, integridad, detalles,idActivo) -> None:
        self.confidencialidad = confidencialidad
        self.disponibilidad = disponibilidad
        self.integridad = integridad
        self.sensibilidad = confidencialidad + disponibilidad + integridad
        self.detalles = detalles
        self.idActivo = idActivo