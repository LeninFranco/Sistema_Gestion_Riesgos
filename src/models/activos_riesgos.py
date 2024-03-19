from src.utils.db import db
from src.models.activos import Activo
from src.models.riesgo import Riesgo

class ActivosRiesgos(db.Model):
    __tablename__ = 'Activos_Riesgos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idActivo = db.Column(db.String(32), db.ForeignKey('Activos.idActivo'))
    idRiesgo = db.Column(db.String(32), db.ForeignKey('Riesgos.idRiesgo'))
    activo = db.relationship('Activo', backref='riesgos_asociados')
    riesgo = db.relationship('Riesgo', backref='activos_asociados')
    probabilidad = db.Column(db.Float)
    impacto = db.Column(db.Float)
    total = db.Column(db.Float)
    umbral = db.Column(db.String(10))

