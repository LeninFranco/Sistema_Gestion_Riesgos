from src.utils.db import db
from datetime import datetime

def getFechaActual():
    return datetime.now().date()

class HistorialAccion(db.Model):
    __tablename__ = 'HistorialAcciones'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False, default=getFechaActual)
    porcentaje = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    detalles = db.Column(db.String(100), nullable=True)
    autor = db.Column(db.String(100), nullable=True)
    idAccion = db.Column(db.String(32), db.ForeignKey('Acciones.idAccion', ondelete='CASCADE'), nullable=False)

    def __init__(self, porcentaje, estado, detalles, autor, idAccion) -> None:
        self.porcentaje = porcentaje
        self.estado = estado
        self.detalles = detalles
        self.autor = autor
        self.idAccion = idAccion