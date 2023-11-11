from src.utils.db import db
from uuid import uuid4

def getDefaultID() -> str:
    return uuid4().hex

def definirUmbral(factor: float) -> str:
    if factor > 0 and factor < 3:
        return "Bajo"
    if factor >= 3 and factor < 6:
        return "Medio"
    if factor >= 6 and factor <= 9:
        return "Alto"

class Riesgo(db.Model):
    __tablename__ = 'Riesgos'
    idRiesgo = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    nombre = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    amenaza = db.Column(db.String(45), nullable=False)
    nivelHabilidad = db.Column(db.Integer, nullable=False)
    motivacion = db.Column(db.Integer, nullable=False)
    oportunidad = db.Column(db.Integer, nullable=False)
    tamaño = db.Column(db.Integer, nullable=False)
    vulnerabilidad = db.Column(db.String(45), nullable=False)
    facilidadDescubrimiento = db.Column(db.Integer, nullable=False)
    facilidadExplotacion = db.Column(db.Integer, nullable=False)
    conciencia = db.Column(db.Integer, nullable=False)
    deteccionIntrusiones = db.Column(db.Integer, nullable=False)
    probabilidad = db.Column(db.Float, nullable=False)
    impactoFinanciero = db.Column(db.Integer, nullable=False)
    impactoReputacion = db.Column(db.Integer, nullable=False)
    impactoLegal = db.Column(db.Integer, nullable=False)
    impactoUsuarios = db.Column(db.Integer, nullable=False)
    impacto = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    umbral = db.Column(db.String(10), nullable=False)
    idTipoRiesgo = db.Column(db.String(32), db.ForeignKey('TiposRiesgo.idTipoRiesgo', ondelete='CASCADE'), nullable=False)
    idActivo = db.Column(db.String(32), db.ForeignKey('Activos.idActivo', ondelete='CASCADE'), nullable=False)

    def __init__(self, nombre, descripcion, amenaza, nivelHabilidad, motivacion, oportunidad, tamaño, vulnerabilidad, facilidadDescubrimiento, facilidadExplotacion, conciencia, deteccionIntrusiones, impactoFinanciero, impactoReputacion, impactoLegal, impactoUsuarios, idTipoRiesgo, idActivo):
        self.nombre = nombre
        self.descripcion = descripcion
        self.amenaza = amenaza
        self.nivelHabilidad = nivelHabilidad
        self.motivacion = motivacion
        self.oportunidad = oportunidad
        self.tamaño = tamaño
        self.vulnerabilidad = vulnerabilidad
        self.facilidadDescubrimiento = facilidadDescubrimiento
        self.facilidadExplotacion = facilidadExplotacion
        self.conciencia = conciencia
        self.deteccionIntrusiones = deteccionIntrusiones
        self.impactoFinanciero = impactoFinanciero
        self.impactoReputacion = impactoReputacion
        self.impactoLegal = impactoLegal
        self.impactoUsuarios = impactoUsuarios
        self.idTipoRiesgo = idTipoRiesgo
        self.idActivo = idActivo

    def priorizarRiesgo(self, sensibilidadActivo: int) -> None:
        factorAmenaza = (self.nivelHabilidad + self.motivacion + self.oportunidad + self.tamaño) / 4
        factorVulnerabilidad = (self.facilidadDescubrimiento + self.facilidadExplotacion + self.conciencia + self.deteccionIntrusiones) / 4
        self.probabilidad = (factorAmenaza + factorVulnerabilidad) / 2
        factorImpactoTecnico = sensibilidadActivo / 3
        factorImpactoEmpresarial = (self.impactoFinanciero + self.impactoReputacion + self.impactoLegal + self.impactoUsuarios) / 4
        self.impacto = (factorImpactoTecnico + factorImpactoEmpresarial) / 2
        self.total = self.probabilidad * self.impacto
        umbralProbabilidad = definirUmbral(self.probabilidad)
        umbralImpacto = definirUmbral(self.impacto)
        """
        if self.impacto <= 5.9:
            if self.probabilidad <= 5.9:
                if self.probabilidad <= 2.9:
                    if self.impacto <= 2.9:
                        self.umbral = 'Insignificante'
                    else:
                        self.umbral = 'Bajo'
                else:
                    if self.impacto <= 2.9:
                        self.umbral = 'Bajo'
                    else:
                        self.umbral = 'Medio'
            else:
                if self.impacto <= 2.9:
                    self.umbral = 'Medio'
                else:
                    self.umbral = 'Alto'
        else:
            if self.probabilidad <= 5.9:
                self.umbral = 'Crítico'
            else:
                if self.probabilidad <= 2.9:
                    self.umbral = 'Medio'
                else:
                    self.umbral = 'Alto'
        """
        if umbralImpacto == 'Bajo' and umbralProbabilidad == 'Bajo':
            self.umbral = 'Insignificante'
        elif umbralImpacto == 'Bajo' and umbralProbabilidad == 'Medio':
            self.umbral = 'Bajo'
        elif umbralImpacto == 'Bajo' and umbralProbabilidad == 'Alto':
            self.umbral = 'Medio'
        elif umbralImpacto == 'Medio' and umbralProbabilidad == 'Bajo':
            self.umbral = 'Bajo'
        elif umbralImpacto == 'Medio' and umbralProbabilidad == 'Medio':
            self.umbral = 'Medio'
        elif umbralImpacto == 'Medio' and umbralProbabilidad == 'Alto':
            self.umbral = 'Alto'
        elif umbralImpacto == 'Alto' and umbralProbabilidad == 'Bajo':
            self.umbral = 'Medio'
        elif umbralImpacto == 'Alto' and umbralProbabilidad == 'Medio':
            self.umbral = 'Alto'
        elif umbralImpacto == 'Alto' and umbralProbabilidad == 'Alto':
            self.umbral = 'Crítico'
        else:
            self.umbral = 'Sin umbral'