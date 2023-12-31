from src.utils.db import db
from src.utils.crypto import bcrypt
from src.models.proyectos import Proyecto
from uuid import uuid4

def getDefaultID() -> str:
    return uuid4().hex

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    idUsuario = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    nombre = db.Column(db.String(50), nullable=False)
    apellidoPaterno = db.Column(db.String(50), nullable=False)
    apellidoMeterno = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(50), nullable=False)
    proyectos = db.relationship('Proyecto', backref='usuario', cascade='all, delete-orphan')

    def __init__(self, nombre, apellidoPaterno, apelidoMaterno, correo, contrasena) -> None:
        self.nombre = nombre
        self.apellidoPaterno = apellidoPaterno
        self.apellidoMeterno = apelidoMaterno
        self.correo = correo
        self.contrasena = bcrypt.generate_password_hash(contrasena)

    def verificarContrasena(self, contrasena) -> bool:
        return bcrypt.check_password_hash(self.contrasena, contrasena)