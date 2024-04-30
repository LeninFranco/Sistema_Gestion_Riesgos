from src.utils.db import db
from datetime import datetime
from sqlalchemy import TEXT

def getFechaActual():
    return datetime.now().date()

class HistorialRiesgo(db.Model):
    __tablename__ = 'HistorialRiesgos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False, default=getFechaActual)
    nivelHabilidad = db.Column(db.Integer, nullable=False)
    motivacion = db.Column(db.Integer, nullable=False)
    oportunidad = db.Column(db.Integer, nullable=False)
    tamaño = db.Column(db.Integer, nullable=False)
    facilidadDescubrimiento = db.Column(db.Integer, nullable=False)
    facilidadExplotacion = db.Column(db.Integer, nullable=False)
    conciencia = db.Column(db.Integer, nullable=False)
    deteccionIntrusiones = db.Column(db.Integer, nullable=False)
    impactoFinanciero = db.Column(db.Integer, nullable=False)
    impactoReputacion = db.Column(db.Integer, nullable=False)
    impactoLegal = db.Column(db.Integer, nullable=False)
    impactoUsuarios = db.Column(db.Integer, nullable=False)
    probabilidad = db.Column(db.Float, nullable=False)
    impacto = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    umbral = db.Column(db.String(255), nullable=False)
    detalles = db.Column(TEXT, nullable=False)
    idRiesgo = db.Column(db.String(32), db.ForeignKey('Riesgos.idRiesgo', ondelete='CASCADE'), nullable=False)

    def __init__(self, nivelHabilidad, motivacion, oportunidad, tamaño, facilidadDescubrimiento, facilidadExplotacion, conciencia, deteccionIntrusiones, impactoFinanciero, impactoReputacion, impactoLegal, impactoUsuarios, probabilidad, impacto, total, umbral, detalles, idRiesgo):
        self.nivelHabilidad = nivelHabilidad
        self.motivacion = motivacion
        self.oportunidad = oportunidad
        self.tamaño = tamaño
        self.facilidadDescubrimiento = facilidadDescubrimiento
        self.facilidadExplotacion = facilidadExplotacion
        self.conciencia = conciencia
        self.deteccionIntrusiones = deteccionIntrusiones
        self.impactoFinanciero = impactoFinanciero
        self.impactoReputacion = impactoReputacion
        self.impactoLegal = impactoLegal
        self.impactoUsuarios = impactoUsuarios
        self.probabilidad = probabilidad
        self.impacto = impacto
        self.total = total
        self.umbral = umbral
        self.detalles = detalles
        self.idRiesgo = idRiesgo