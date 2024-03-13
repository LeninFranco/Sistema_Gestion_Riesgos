from src.utils.db import db
from src.utils.crypto import bcrypt
from uuid import uuid4

def getDefaultID() -> str:
    return uuid4().hex

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    idUsuario = db.Column(db.String(32), primary_key=True, default=getDefaultID)
    nombre = db.Column(db.String(50), nullable=False)
    apellidoPaterno = db.Column(db.String(50), nullable=False)
    apellidoMaterno = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    telefono = db.Column(db.String(15), unique=True, nullable=False)
    contrasena = db.Column(db.String(50), nullable=False)
    departamento = db.Column(db.String(30), nullable=False)
    cargo = db.Column(db.String(30), nullable=False)
    rol = db.Column(db.Integer, nullable=False)
    idJefe = db.Column(db.String(32), db.ForeignKey('Usuarios.idUsuario'))

    def __init__(self, nombre, apellidoPaterno, apelidoMaterno, correo, telefono, departamento, cargo, contrasena, rol, idJefe=None) -> None:
        self.nombre = nombre
        self.apellidoPaterno = apellidoPaterno
        self.apellidoMaterno = apelidoMaterno
        self.correo = correo
        self.telefono = telefono
        self.departamento = departamento
        self.cargo = cargo
        self.contrasena = bcrypt.generate_password_hash(contrasena)
        self.rol = rol
        self.idJefe = idJefe

    def verificarContrasena(self, contrasena) -> bool:
        return bcrypt.check_password_hash(self.contrasena, contrasena)