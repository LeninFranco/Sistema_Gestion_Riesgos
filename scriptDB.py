from src.models.usuarios import Usuario
from src.models.activos import Activo
from src.utils.db import db
from app import app
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def generarChalanes(idJefe):
    departamentos = ["Desarrollo de Software", "Diseño UX/UI", "Calidad de Software", "Gestión de Proyectos", "Soporte Técnico", "Redes", "Bases de Datos"]
    cargos = ["Desarrollador Backend", "Desarrollador Frontend", "Diseñador UX/UI", "Tester de Software", "Project Manager", "Soporte Técnico", "Administrador de Redes", "Administrador de Bases de Datos"]
    for _ in range(20):
        nombre = fake.first_name()
        apellido_paterno = fake.last_name()
        apellido_materno = fake.last_name()
        correo = fake.email()
        telefono = f"{random.choice(['55', '56'])}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
        departamento = random.choice(departamentos)
        cargo = random.choice(cargos)
        contrasena = fake.password(length=12)
        rol = 1
        idJefe = idJefe
        usuario = Usuario(nombre, apellido_paterno, apellido_materno, correo, telefono, departamento, cargo, contrasena, rol, idJefe)
        db.session.add(usuario)
        db.session.commit()

def generarActivos(idProyecto, subnumero):
    frecuencias = ['No Requiere','Diario','Semanal','Quincenal','Mensual','Bimestral','Trimestral','Semestral','Anual']
    tipos_activo = ['Información/Documentos','Aplicaciones','Plataformas','Bases de Datos','Red/Telecomunicaciones','Intangibles','Gente/Personal','Físico']
    departamentos = ["Desarrollo de Software", "Diseño UX/UI", "Calidad de Software", "Gestión de Proyectos", "Soporte Técnico", "Redes", "Bases de Datos"]
    for i in range(30):
        clave = f"AP{subnumero}-{str(i+1).zfill(4)}"
        nombre = f"Activo {i+1}"
        descripcion = f"Descripción del activo {i+1}"
        propietario = f"Propietario {i+1}"
        ubicacion = 'Departamento de ' + random.choice(departamentos)
        frec_mantenimiento = random.choice(frecuencias)
        frec_renovacion = random.choice(frecuencias)
        fecha_adquisicion = datetime.now() - timedelta(days=random.randint(365, 365*5))  # Fecha aleatoria en los últimos 5 años
        fecha_adquisicion = fecha_adquisicion.replace(hour=0, minute=0, second=0, microsecond=0)
        tipo_activo = random.choice(tipos_activo)
        estatus = "En uso"
        confidencialidad = random.randint(1, 9)
        disponibilidad = random.randint(1, 9)
        integridad = random.randint(1, 9)
        activo = Activo(clave, nombre, descripcion, propietario, ubicacion, frec_mantenimiento, frec_renovacion, fecha_adquisicion, tipo_activo, estatus, idProyecto)
        activo.evaluarActivo(confidencialidad,disponibilidad,integridad)
        db.session.add(activo)
    db.session.commit()


with app.app_context():
    pass