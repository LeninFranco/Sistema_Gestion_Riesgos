from src.models.usuarios import Usuario
from src.models.activos import Activo
from src.models.riesgo import Riesgo
from src.models.proyectos import Proyecto
from src.models.activos_riesgos import ActivosRiesgos
from src.utils.db import db
from app import app
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def definirUmbral(factor: float) -> str:
    if factor > 0 and factor < 3:
        return "Bajo"
    if factor >= 3 and factor < 6:
        return "Medio"
    if factor >= 6 and factor <= 9:
        return "Alto"

def obtenerProbabilidad(riesgo) -> float:
    amenazaRiesgo = (riesgo.nivelHabilidad + riesgo.motivacion + riesgo.oportunidad + riesgo.tamaño)/4
    vulnerabilidadRiesgo = (riesgo.facilidadDescubrimiento + riesgo.facilidadExplotacion + riesgo.conciencia + riesgo.deteccionIntrusiones)/4
    prob = (amenazaRiesgo + vulnerabilidadRiesgo)/2
    return prob

def obtenerImpacto(riesgo, activo) -> float:
    impactoEmpresarialRiesgo = (riesgo.impactoFinanciero + riesgo.impactoReputacion + riesgo.impactoLegal + riesgo.impactoUsuarios)/4
    impactoTecnicoActivo = (activo.sensibilidad)/3
    imp = (impactoEmpresarialRiesgo + impactoTecnicoActivo)/2
    return imp

def obtenerTotal(probabildad: float, impacto: float) -> float:
    return probabildad * impacto

def obtenerUmbral(probabilidad: float, impacto: float) -> str:
    umbralProb = definirUmbral(probabilidad)
    umbralImp = definirUmbral(impacto)
    if umbralImp == 'Bajo' and umbralProb == 'Bajo':
            umbral = 'Insignificante'
    elif umbralImp == 'Bajo' and umbralProb == 'Medio':
        umbral = 'Bajo'
    elif umbralImp == 'Bajo' and umbralProb == 'Alto':
        umbral = 'Medio'
    elif umbralImp == 'Medio' and umbralProb == 'Bajo':
        umbral = 'Bajo'
    elif umbralImp == 'Medio' and umbralProb == 'Medio':
        umbral = 'Medio'
    elif umbralImp == 'Medio' and umbralProb == 'Alto':
        umbral = 'Alto'
    elif umbralImp == 'Alto' and umbralProb == 'Bajo':
        umbral = 'Medio'
    elif umbralImp == 'Alto' and umbralProb == 'Medio':
        umbral = 'Alto'
    elif umbralImp == 'Alto' and umbralProb == 'Alto':
        umbral = 'Crítico'
    else:
        umbral = 'Sin umbral'
    return umbral

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

def generarActivosRiesgos(idProyecto, subnumero):
    frecuencias = ['No Requiere','Diario','Semanal','Quincenal','Mensual','Bimestral','Trimestral','Semestral','Anual']
    tipos_activo = ['Información/Documentos','Aplicaciones','Plataformas','Bases de Datos','Red/Telecomunicaciones','Intangibles','Gente/Personal','Físico']
    departamentos = ["Desarrollo de Software", "Diseño UX/UI", "Calidad de Software", "Gestión de Proyectos", "Soporte Técnico", "Redes", "Bases de Datos"]
    tipos_riesgos = ['Lógico', 'Físico', 'Organizacional']
    agentes_amenaza = [
    'Hackers',
    'Ciberdelincuentes',
    'Estado-Nación',
    'Empleados Descontentos o Desleales',
    'Activistas Cibernéticos',
    'Competidores Comerciales',
    'Usuarios Malintencionados Internos',
    'Bots y Botnets',
    'Grupos de Crimen Organizado'
]
    activos = []
    riesgos = []
    asociaciones = []
    #Generación de activos
    for i in range(30):
        clave = f"APSW{subnumero}-{str(i+1).zfill(4)}"
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
        activos.append(activo)
    
    #Generación de riesgos
    for i in range(50):
        clave = f'RPSW{subnumero}-{str(i+1).zfill(4)}'
        nombre = f'Riesgo {i+1}'
        descripcion = f"Descripción del Riesgo {i+1}"
        tipo = random.choice(tipos_riesgos)
        nivelHabilidad = random.randint(1, 9)
        motivacion = random.randint(1, 9)
        oportunidad = random.randint(1, 9)
        tamaño = random.randint(1, 9)
        facilidadDescubrimiento = random.randint(1, 9)
        facilidadExplotacion = random.randint(1, 9)
        conciencia = random.randint(1, 9)
        deteccionIntrusiones = random.randint(1, 9)
        impactoFinanciero = random.randint(1, 9)
        impactoReputacion = random.randint(1, 9)
        impactoLegal = random.randint(1, 9)
        impactoUsuarios = random.randint(1, 9)
        amenaza = random.choice(agentes_amenaza)
        riesgo = Riesgo(clave, nombre, descripcion, tipo, amenaza, nivelHabilidad, motivacion, oportunidad, tamaño, 'Vulnerabilidad X', facilidadDescubrimiento, facilidadExplotacion,conciencia, deteccionIntrusiones, impactoFinanciero, impactoReputacion, impactoLegal, impactoUsuarios)
        riesgos.append(riesgo)

    #Generar asociaciones
    for activo in activos:
        riesgos_a = random.sample(riesgos, 3)
        asociaciones.append((activo, ) + tuple(riesgos_a))
    for asociacion in asociaciones:
        for i in range(1,4,1):
            probabilidadRiesgo = obtenerProbabilidad(asociacion[i])
            impactoRiesgoActivo = obtenerImpacto(asociacion[i], asociacion[0])
            a = ActivosRiesgos(riesgo = asociacion[i], activo = asociacion[0], probabilidad = probabilidadRiesgo, impacto = impactoRiesgoActivo, total = obtenerTotal(probabilidadRiesgo,impactoRiesgoActivo), umbral = obtenerUmbral(probabilidadRiesgo,impactoRiesgoActivo))
            db.session.add(a)
    db.session.commit()

def obtenerTareasSinAsignar(idProyecto):
    proyecto = Proyecto.query.filter_by(idProyecto = idProyecto).first()
    activos = proyecto.activos
    riesgos = []
    tareas = []
    
    for activo in activos:
        for asociacion in activo.riesgos_asociados:
            riesgos.append(asociacion.riesgo)     
    riesgos_umbrales = []
    dictRiesgos = {}
    for activo in activos:
        for asociacion in activo.riesgos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos: #Si el riesgo aun no esta en el diccionario lo añadimos
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,  #Para tener el objeto del riesgo para sus detalles
                    'activos' : [ (asociacion.activo, definirUmbral(obtenerProbabilidad(asociacion.riesgo)), definirUmbral(obtenerImpacto(asociacion.riesgo,asociacion.activo)), asociacion.umbral, asociacion.total) ]
                }
            else:
                dictRiesgos[asociacion.riesgo.clave]['activos'].append( (asociacion.activo, definirUmbral(obtenerProbabilidad(asociacion.riesgo)), definirUmbral(obtenerImpacto(asociacion.riesgo,asociacion.activo)), asociacion.umbral, asociacion.total) ) #La lista de activos con la que esta asociado el riesgo con sus valores
    
    for clave in dictRiesgos.keys():
        riesgo = dictRiesgos[clave]['riesgo']
        for accion in riesgo.acciones:
            if accion.idParticipante == None:
                tareas.append(accion)
    
    for tarea in tareas:
        print(tarea.clave)



with app.app_context():
    generarActivosRiesgos('aae39ecc16e744f3ae0038c1a31b2367', 1)