from flask import Blueprint, session, redirect, url_for, render_template, request, flash, jsonify
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.activos import Activo
from src.models.riesgo import Riesgo
from src.models.responsables import Participantes
from src.models.activos_riesgos import ActivosRiesgos
from src.models.acciones import Accion
from src.models.historialAcciones import HistorialAccion
from datetime import datetime

acciones = Blueprint('acciones', __name__)

def definirUmbral(factor: float) -> str:
    if factor > 0 and factor < 3:
        return "Bajo"
    if factor >= 3 and factor < 6:
        return "Medio"
    if factor >= 6 and factor <= 9:
        return "Alto"

categoriasISO27001 = {
    "5": "Política de seguridad",
    "6": "Organización de seguridad de la información",
    "7": "Administración de activos",
    "8": "Seguridad de los recursos humanos",
    "9": "Seguridad física y del ambiente ",
    "10": "Administración de las comunicaciones y operaciones",
    "11": "Control de acceso",
    "12": "Adquisición, desarrollo y mantenimiento de sistemas de información",
    "13": "Administración de inicidentes de seguridad de la información",
    "14": "Administración de la continuidad del negocio",
    "15": "Cumplimiento"
}

controlesISO27001 = {
    #5 Política de seguridad 
    "5": {
        "5.1": "Política de seguridad de la información",
        "5.1.1": "Documento de la política de seguridad de la información",
        "5.1.2": "Revisar la política de seguridad de la información"
    },
    #6. Organización de seguridad de la información 
    "6":{
        "6.1": "Organización interna",
        "6.1.1": "Compromiso de la Alta Dirección con la seguridad de la información",
        "6.1.2": "Coordinación de la seguridad de la información",
        "6.1.3": "Asignación de responsabilidades de seguridad de la información",
        "6.1.4": "Proceso de autorización para instalaciones de procesamiento de información",
        "6.1.5": "Acuerdos de confidencialidad",
        "6.1.6": "Contacto con las autoridades",
        "6.1.7": "Contacto con grupos de interés especial",
        "6.1.8": "Revisión independiente de la seguridad de la información",
        "6.2": "Partes Externas",
        "6.2.1": "Identificación de riesgos relacionados con partes externas",
        "6.2.2": "Tratamiento de la seguridad al tratar con clientes",
        "6.2.3": "Tratamiento de la seguridad en acuerdos con terceros"
    },
    #7. Administración de activos 
    "7" :{
        "7.1": "Responsabilidad de activos",
        "7.1.1": "Inventario de activos",
        "7.1.2": "Propiedad de los activos",
        "7.1.3": "Uso aceptable de activos",
        "7.2": "Clasificación de información",
        "7.2.1": "Guías de clasificación",
        "7.2.2": "Etiquetado y manejo de la información"
    },
    #8 Seguridad de los recursos humanos  
    "8" :{
        "8.1": "Previo a la contratación",
        "8.1.1": "Roles y responsabilidades",
        "8.1.2": "Investigación de antecedentes",
        "8.1.3": "Términos y condiciones de contratación",
        "8.2": "Durante el empleo",
        "8.2.1": "Responsabilidades de la Alta Dirección",
        "8.2.2": "Concientización, capacitación y entrenamiento en seguridad de la información",
        "8.2.3": "Proceso disciplinario",
        "8.3": "Terminación o cambio de empleo",
        "8.3.1": "Responsabilidades de terminación ",
        "8.3.2": "Devolución de activos",
        "8.3.3": "Eliminación de los derechos de acceso"
    },
    #9 Seguridad física y del ambiente 
    "9" :{
        "9.1": "Áreas seguras",
        "9.1.1": "Perímetro físico de la seguridad",
        "9.1.2": "Controles de entrada física",
        "9.1.3": "Seguridad en las oficinas, cuartos e instalaciones",
        "9.1.4": "Protección contra amenazas externas y ambientales",
        "9.1.5": "Trabajo en áreas seguras",
        "9.1.6": "Áreas de acceso público, entrega y carga",
        "9.2": "Seguridad de equipo",
        "9.2.1": "Situado y protección de equipo",
        "9.2.2": "Servicios de soporte",
        "9.2.3": "Seguridad en el cableado",
        "9.2.4": "Mantenimiento de equipo",
        "9.2.5": "Seguridad del equipo fuera de las instalaciones",
        "9.2.6": "Desecho o reuso seguro del equipo",
        "9.2.7": "Retiro de propiedad"
    },
    #10 Administración de las comunicaciones y operaciones  
    "10" :{
        "10.1": "Responsabilidades y procedimientos de operación",
        "10.1.1": "Procedimientos de operación documentados",
        "10.1.2": "Administración de cambios",
        "10.1.3": "Segregación de deberes",
        "10.1.4": "Separación de las instalaciones de desarrollo, pruebas y operación.",
        "10.2": "Administración de entrega de servicios de terceros",
        "10.2.1": "Entrega de servicio",
        "10.2.2": "Monitoreo y revisión de servicios de terceros",
        "10.2.3": "Administración de cambios en servicios de terceros",
        "10.3": "Planeación y aceptación de sistemas",
        "10.3.1": "Administración de capacidad",
        "10.3.2": "Aceptación de sistemas",
        "10.4": "Protección contra código malicioso y móvil",
        "10.4.1": "Controles contra código malicioso",
        "10.4.2": "Controles contra código móvil",
        "10.5": "Respaldos",
        "10.5.1": "Respaldo de información",
        "10.6": "Administración de la seguridad de redes",
        "10.6.1": "Controles de red",
        "10.6.2": "Seguridad de los servicios de red",
        "10.7": "Manejo de medios",
        "10.7.1": "Administración de medios removibles",
        "10.7.2": "Desecho de medios",
        "10.7.3": "Procedimientos de manejo de información",
        "10.7.4": "Seguridad de la documentación de sistemas",
        "10.8": "Intercambio de información",
        "10.8.1": "Políticas y procedimientos de intercambio de información"
    },
    #11 Control de acceso   
    "11" :{
        "11.1": "Requerimientos del negocio para el control de acceso",
        "11.1.1": "Política de control de acceso",
        "11.2": "Administración de acceso de usuarios",
        "11.2.1": "Registro de usuarios",
        "11.2.2": "Administración de privilegios",
        "11.2.3": "Administración de contraseñas de usuarios",
        "11.2.4": "Revisión de derechos de acceso de usuarios",
        "11.3": "Responsabilidades de los usuarios",
        "11.3.1": "Uso de contraseñas",
        "11.3.2": "Equipo de usuarios desatendido",
        "11.3.3": "Política de escritorio y pantalla despejados",
        "11.4": "Control de acceso a la red",
        "11.4.1": "Política de uso de servicios de red",
        "11.4.2": "Autentificación de usuarios para conexiones externas",
        "11.4.3": "Identificación de equipos en redes",
        "11.4.4": "Protección para los puertos de diagnóstico y configuración remotos",
        "11.4.5": "Segregación en redes",
        "11.4.6": "Control de conexiones de red",
        "11.4.7": "Control de ruteo de red",
        "11.5": "Control de acceso a los sistemas operativos",
        "11.5.1": "Procedimientos seguros de inicio de sesión",
        "11.5.2": "Identificación y autentificación de usuarios",
        "11.5.3": "Sistema de administración de contraseñas",
        "11.5.4": "Uso de utilerías de sistema",
        "11.5.5": "Expiración de sesión",
        "11.5.6": "Limitación del tiempo de conexión",
        "11.6": "Control de acceso a aplicaciones e información",
        "11.6.1": "Restricción de acceso a la información",
        "11.6.2": "Aislamiento de sistemas sensibles",
        "11.7": "Cómputo móvil y trabajo remoto",
        "11.7.1": "Cómputo y comunicaciones móviles",
        "11.7.2": "Trabajo remoto"
    },
    #12 Adquisición, desarrollo y mantenimiento de sistemas de información
    "12" :{
        "12.1": "Requerimientos de seguridad de los sistemas de información",
        "12.1.1": "Análisis y especificación de los requerimientos de seguridad",
        "12.2": "Procesamiento correcto en aplicaciones",
        "12.2.1": "Validación de los datos de entrada",
        "12.2.2": "Control de procesamiento interno",
        "12.2.3": "Integridad de mensajes",
        "12.2.4": "Validación de los datos de salida",
        "12.3": "Controles criptográficos",
        "12.3.1": "Política del uso de controles criptográficos",
        "12.3.2": "Administración de llaves",
        "12.4": "Seguridad de archivos de sistema",
        "12.4.1": "Control de software de operación",
        "12.4.2": "Protección de datos de pruebas de sistemas",
        "12.4.3": "Control de acceso a código fuente de programas",
        "12.5": "Seguridad en los procesos de desarrollo y soporte",
        "12.5.1": "Procedimientos de control de cambios",
        "12.5.2": "Revisión técnica de aplicaciones después de cambios en el sistema operativo",
        "12.5.3": "Restricciones en cambios a los paquetes de software",
        "12.5.4": "Fuga de información",
        "12.5.5": "Desarrollo subcontratado de software",
        "12.6": "Administración de vulnerabilidades técnicas",
        "12.6.1": "Control de vulnerabilidades técnicas"
    },
    #13 Administración de inicidentes de seguridad de la información
    "13" :{
        "13.1": "Reporte de eventos y debilidades de seguridad de la información",
        "13.1.1": "Reporte de los eventos de seguridad de la información",
        "13.1.2": "Reporte de las debilidades de seguridad",
        "13.2": "Administración de incidentes y mejoras de seguridad de la información",
        "13.2.1": "Responsabilidades y procedimientos",
        "13.2.2": "Aprendizaje de los incidentes de seguridad informática",
        "13.2.3": "Recopilación de evidencia"
    },
    #14 Administración de la continuidad del negocio 
    "14" :{
        "14.1": "Aspectos de seguridad de la información de la Administración de la Continuidad del Negocio",
        "14.1.1": "Incluir la seguridad de la información en el proceso de administración de continuidad de negocio",
        "14.1.2": "Continuidad de negocio y evaluación de riesgo",
        "14.1.3": "Desarrollo e implementación de planes de continuidad incluyendo la seguridad de la información",
        "14.1.4": "Marco de referencia de la planeación de la continuidad de negocio",
        "14.1.5": "Pruebas, mantenimiento y reevaluación de los planes de continuidad de negocio"
    },
    #15 Cumplimiento
    "15" :{
        "15.1": "Cumplimiento con los requerimientos legales",
        "15.1.1": "Identificación de legislación aplicable",
        "15.1.2": "Derechos de propiedad intelectual (IPR, intellectual property rights)",
        "15.1.3": "Protección de registros organizacionales",
        "15.1.4": "Protección de datos y privacidad de información personal",
        "15.1.5": "Prevención del uso incorrecto de las instalaciones de procesamiento de información",
        "15.1.6": "Regulación de controles criptográficos",
        "15.2": "Cumplimiento con políticas y estándares de seguridad y cumplimiento técnico",
        "15.2.1": "Cumplimiento con las políticas y estándares de seguridad",
        "15.2.2": "Comprobación de cumplimiento técnico",
        "15.3": "Consideración para las auditorías de sistemas de información",
        "15.3.1": "Controles de auditoría de los sistemas de información",
        "15.3.2": "Protección de las herramientas de auditoría de sistemas de información"
    }
}


categoriasISO27002 = {
    "5": "Controles organizacionales",
    "6": "Controles de personas",
    "7": "Controles físicos",
    "8": "Controles tecnológicos"
}


controlesISO27002 = {
    #5. Controles organizacionales 
    "5": {
        "5.1": "Políticas de seguridad de la información",
        "5.2": "Funciones y responsabilidades en materia de seguridad de la información",
        "5.3": "Segregación de funciones",
        "5.4": "Responsabilidades de la dirección",
        "5.5": "Contacto con las autoridades",
        "5.6": "Contacto con grupos de interés especiales",
        "5.7": "Información sobre amenazas",
        "5.8": "Seguridad de la información en la gestión de proyectos",
        "5.9": "Inventario de la información y otros activos asociados",
        "5.10": "Uso aceptable de la información y otros activos asociados",
        "5.11": "Devolución de activos",
        "5.12": "Clasificación de la información",
        "5.13": "Etiquetado de la información",
        "5.14": "Transferencia de información",
        "5.15": "Control de acceso",
        "5.16": "Gestión de identidades",
        "5.17": "Información de autenticación",
        "5.18": "Derechos de acceso",
        "5.19": "Seguridad de la información en las relaciones con los proveedores",
        "5.20": "Tratamiento de la seguridad de la información en los acuerdos con proveedores",
        "5.21": "Gestión de la seguridad de la información en la cadena de suministro de TIC",
        "5.22": "Monitoreo, revisión y gestión de cambios de los servicios de proveedores",
        "5.23": "Seguridad de la información para el uso de servicios en la nube",
        "5.24": "Planificación y preparación de la gestión de incidentes de seguridad de la información",
        "5.25": "Valoración y decisión sobre incidentes de seguridad de la información"
    },
    #6. Controles de personas
    "6":{

        "6.1": "Investigación",
        "6.2": "Condiciones de empleo",
        "6.3": "Sensibilización, educación y formación en materia de seguridad de la información",
        "6.4": "Proceso disciplinario",
        "6.5": "Responsabilidades tras el cese o cambio de empleo",
        "6.6": "Acuerdos de confidencialidad o no divulgación",
        "6.7": "Trabajo a distancia",
        "6.8": "Notificación de sucesos relacionados con la seguridad de la información    "
    },
    #7. Controles físicos 
    "7" :{
        "7.1": "Perímetros de seguridad física",
        "7.2": "Entrada física",
        "7.3": "Seguridad de oficinas, salas e instalaciones",
        "7.4": "Supervisión de la seguridad física",
        "7.5": "Protección contra amenazas físicas y ambientales",
        "7.6": "Trabajar en zonas seguras",
        "7.7": "Escritorio y pantalla despejados",
        "7.8": "Ubicación y protección de los equipos",
        "7.9": "Seguridad de los activos fuera de las instalaciones",
        "7.10": "Medios de almacenamiento",
        "7.11": "Servicios de apoyo",
        "7.12": "Seguridad del cableado",
        "7.13": "Mantenimiento de los equipos",
        "7.14": "Seguridad en la eliminación o reutilización de equipos."
    },
    #8 Controles tecnológicos 
    "8" :{
        "8.1": "Dispositivos de usuario",
        "8.2": "Derechos de acceso privilegiado",
        "8.3": "Restricción del acceso a la información",
        "8.4": "Acceso al código fuente",
        "8.5": "Autenticación segura",
        "8.6": "Gestión de la capacidad",
        "8.7": "Protección contra el malware",
        "8.8": "Gestión de vulnerabilidades técnicas",
        "8.9": "Gestión de la configuración",
        "8.10": "Borrado de información",
        "8.11": "Enmascaramiento de datos",
        "8.12": "Prevención de la fuga de datos",
        "8.13": "Copia de seguridad de la información",
        "8.14": "Redundancia de las instalaciones de tratamiento de la información",
        "8.15": "Registro de datos",
        "8.16": "Actividades de supervisión",
        "8.17": "Sincronización de relojes",
        "8.18": "Uso de programas de utilidades privilegiadas",
        "8.19": "Instalación de software en sistemas operativos",
        "8.20": "Seguridad de las redes",
        "8.21": "Seguridad de los servicios de red",
        "8.22": "Segregación de redes",
        "8.23": "Filtrado web",
        "8.24": "Uso de criptografía",
        "8.25": "Ciclo de vida del desarrollo seguro",
        "8.26": "Requisitos de seguridad de las aplicaciones",
        "8.27": "Arquitectura de sistemas seguros y principios de ingeniería",
        "8.28": "Codificación segura",
        "8.29": "Pruebas de seguridad en el desarrollo y la aceptación",
        "8.30": "Desarrollo externalizado",
        "8.31": "Separación de los entornos de desarrollo, prueba y producción",
        "8.32": "Gestión de cambios",
        "8.33": "Información de las pruebas",
        "8.34": "Protección de los sistemas de información durante las pruebas de auditoría"
    }
}

objetivos = {
    "Aceptar": "Asumir el riesgo",
    "Modificar": "Reducir la probabilidad y el impacto del riesgo",
    "Trasladar": "Compartir el riesgo con un tercero que pueda tratarlo",
    "Evitar": "Eliminar aquello que causa el riesgo"
    }



estadosAccion = [
    "En proceso",
    "Hecho",
    "Cancelada",
    "Pospuesto",
    "En revisión"
]

@acciones.route('/listar-acciones')
def vistaListaAcciones():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos #Necesitamos los activos para obtener sus riesgos, y saber cualess riesgos no tienen tareas
    participantes_jefe = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    participantes_proyecto = []
    for asociacion in proyecto.usuarios_asociados:
        if not asociacion.estado == 'Suspendido':
            participantes_proyecto.append((asociacion.usuario, asociacion.estado))
    usuarios_listado = []
    for participante in participantes_jefe:
        if participante in [x[0] for x in participantes_proyecto]:
            usuarios_listado.append(participante)


    acciones = []

    
    for asociacion in proyecto.usuarios_asociados:
        if asociacion.acciones:
            for actions in asociacion.acciones:
                risk = Riesgo.query.filter_by(idRiesgo = actions.idRiesgo).first()
                acciones.append(((actions,asociacion.usuario,risk)))

    #Diccionario de riesgos para tener solo un riesgo por n activos, no necesitamos manejar el activo, solo el riesgo
    dictRiesgos = {}
    for activo in activos:
        for asociacion in activo.riesgos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos: #Si el riesgo aun no esta en el diccionario lo añadimos
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,  #Para tener el objeto del riesgo para sus detalles
                    'activos' : [ (asociacion.activo, definirUmbral(obtenerProbabilidad(asociacion.riesgo)), definirUmbral(obtenerImpacto(asociacion.riesgo,asociacion.activo)), asociacion.umbral, asociacion.total) ]
                }
    #Diccionario de riesgos siwn accioness
    dictRiesgosSinAcciones = []
    for clave in dictRiesgos.keys():
        if len(dictRiesgos[clave]['riesgo'].acciones) < 1:
            dictRiesgosSinAcciones.append(dictRiesgos[clave]['riesgo'])
    return render_template('acciones/listaAcciones.html', usuario=usuario, acciones=acciones, dictRiesgos = dictRiesgos, dictRiesgosSinAcciones = dictRiesgosSinAcciones, estadosAccion = estadosAccion, objetivos = objetivos, usuarios_listado = usuarios_listado, controlesISO27001 = controlesISO27001,categoriasISO27001 = categoriasISO27001, participantes_proyecto = participantes_proyecto)

@acciones.route('/modificar-accion/<string:idAccion>')
def vistaModificacionAccion(idAccion):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    accion = Accion.query.filter_by(idAccion=idAccion).first()
    activos = proyecto.activos
    participantes_proyecto = []
    participantes_jefe = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    participantes_proyecto = []
    for asociacion in proyecto.usuarios_asociados:
        if not asociacion.estado == 'Suspendido':
            participantes_proyecto.append((asociacion.usuario, asociacion.estado))
    usuarios_listado = []
    for participante in participantes_jefe:
        if participante in [x[0] for x in participantes_proyecto]:
            usuarios_listado.append(participante)


    acciones = []

    
    for asociacion in proyecto.usuarios_asociados:
        for actions in asociacion.acciones:
            acciones.append(actions)

    #Diccionario de riesgos para tener solo un riesgo por n activos, no necesitamos manejar el activo, solo el riesgo
    dictRiesgos = {}
    for activo in activos:
        for asociacion in activo.riesgos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos: #Si el riesgo aun no esta en el diccionario lo añadimos
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,  #Para tener el objeto del riesgo para sus detalles
                    #'activos' : [ (asociacion.activo, definirUmbral(obtenerProbabilidad(asociacion.riesgo)), definirUmbral(obtenerImpacto(asociacion.riesgo,asociacion.activo)), asociacion.umbral, asociacion.total) ]
                }
    #Diccionario de riesgos siwn accioness
    dictRiesgosSinAcciones = []
    for clave in dictRiesgos.keys():
        if len(dictRiesgos[clave]['riesgo'].acciones) < 1:
            dictRiesgosSinAcciones.append(dictRiesgos[clave]['riesgo'])
            
    
    
    descripcionControl = controlesISO27001[accion.categoria][accion.control]
    return render_template('acciones/edicionAccion.html', accion = accion ,usuario=usuario, acciones=acciones, dictRiesgos = dictRiesgos, dictRiesgosSinAcciones = dictRiesgosSinAcciones, estadosAccion = estadosAccion, objetivos = objetivos, usuarios_listado = usuarios_listado, controlesISO27001 = controlesISO27001,categoriasISO27001 = categoriasISO27001, descripcionControl = descripcionControl)

@acciones.route('/anadir-accion', methods=['POST'])
def añadirAccion():
    if request.method == 'POST':
        
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            fechaIni = request.form['fechaIni']
            fechaFin = request.form['fechaFin']
            fechaAviso = request.form['fechaAviso']
            objetivo = request.form['objetivo']
            categoria = request.form['categoria']
            control = request.form['control']
            #porcentaje = request.form['porcentaje']
            #estado = request.form['estado']
            #detalles = request.form['detalles']
            idUsuario = request.form['idUsuario']
            idRiesgo = request.form['idRiesgo']
            proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
            participante = Participantes.query.filter_by(idUsuario = idUsuario, idProyecto = proyecto.idProyecto).first()
            acc = Accion(
                clave=clave,
                nombre=nombre,
                descripcion=descripcion,
                fechaIni=datetime.strptime(fechaIni, '%Y-%m-%d').date(),
                fechaFin=datetime.strptime(fechaFin, '%Y-%m-%d').date(),
                objetivo=objetivo,
                fechaAviso=datetime.strptime(fechaAviso, '%Y-%m-%d').date(),
                categoria = categoria,
                control = control,
                porcentaje = float(0),
                estado = "Iniciado",
                detalles = '',
                idParticipante = participante.id,
                idRiesgo = idRiesgo
            )
            db.session.add(acc)
            db.session.commit()
            flash('success')
            flash('La acción ha sido añadida correctamente')
        
    return redirect(url_for('acciones.vistaListaAcciones'))

@acciones.route('/actualizar-accion', methods=['POST'])
def actualizarAccion():
    if request.method == 'POST':
        idAccion = request.form['idAccion']
        clave = request.form['clave']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        fechaIniStr = request.form['fechaIni']
        fechaFinStr = request.form['fechaFin']
        fechaAviso = request.form['fechaAviso']
        fechaIni = datetime.strptime(fechaIniStr, '%Y-%m-%d')
        fechaFin = datetime.strptime(fechaFinStr, '%Y-%m-%d')
        objetivo = request.form['objetivo']
        categoria = request.form['categoria']
        control = request.form['control']
        porcentaje = request.form['porcentaje']
        estado = request.form['estado']
        detalles = request.form['detalles']
        idUsuario = request.form['idUsuario']
        idRiesgo = request.form['idRiesgo']
        proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
        participante = Participantes.query.filter_by(idUsuario = idUsuario, idProyecto = proyecto.idProyecto).first()
        acc = Accion.query.filter_by(idAccion=idAccion).first()
        acc.clave=clave
        acc.nombre=nombre
        acc.descripcion=descripcion
        acc.fechaIni=fechaIni.date()
        acc.fechaFin=fechaFin.date()
        acc.fechaAviso=datetime.strptime(fechaAviso, '%Y-%m-%d').date()
        acc.objetivo=objetivo
        acc.categoria=categoria
        acc.control=control
        acc.porcentaje=float(porcentaje)
        acc.estado=estado
        acc.detalles=detalles
        acc.idRiesgo=idRiesgo
        acc.idParticipante=participante.id      
        db.session.add(acc)
        db.session.commit()
        flash('success')
        flash('La acción ha sido actualizada correctamente')
        return redirect(url_for('acciones.vistaListaAcciones'))

@acciones.route('/eliminar-accion/<string:idAccion>')
def eliminarRiesgo(idAccion):
    acc = Accion.query.filter_by(idAccion=idAccion).first()
    db.session.delete(acc)
    db.session.commit()
    flash('danger')
    flash('La acción fue eliminada exitosamente') 
    return redirect(url_for('acciones.vistaListaAcciones'))

@acciones.route('/listar-sin-asignar')
def vistaListaAccionesSinAsignar():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    participantes_jefe = Usuario.query.filter_by(idJefe = usuario.idUsuario).all()
    participantes_proyecto = []
    for asociacion in proyecto.usuarios_asociados:
        if not asociacion.estado == 'Suspendido':
            participantes_proyecto.append((asociacion.usuario, asociacion.estado))
    usuarios_listado = []
    for participante in participantes_jefe:
        if participante in [x[0] for x in participantes_proyecto]:
            usuarios_listado.append(participante)
    dictRiesgos = {}
    for activo in activos:
        for asociacion in activo.riesgos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos: #Si el riesgo aun no esta en el diccionario lo añadimos
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,  #Para tener el objeto del riesgo para sus detalles
                    'activos' : [ (asociacion.activo, definirUmbral(obtenerProbabilidad(asociacion.riesgo)), definirUmbral(obtenerImpacto(asociacion.riesgo,asociacion.activo)), asociacion.umbral, asociacion.total) ]
                }
    acciones = []
    for clave in dictRiesgos.keys():
        for accion in dictRiesgos[clave]['riesgo'].acciones:
            if accion.idParticipante == None:
                risk = Riesgo.query.filter_by(idRiesgo = accion.idRiesgo).first()
                acciones.append(((accion,risk)))
    return render_template('acciones/listaAccionesSinA.html', usuario=usuario, usuarios_listado=usuarios_listado, acciones=acciones, dictRiesgos = dictRiesgos)

@acciones.route('/asignar-participante', methods=['POST'])
def asignarNuevoParticipante():
    if request.method == 'POST':
        idAccion = request.form['idAccion']
        idUsuario = request.form['responsable']
        accion = Accion.query.filter_by(idAccion=idAccion).first()
        Participante = Participantes.query.filter_by(idUsuario=idUsuario, idProyecto=session['proyecto_id']).first()
        accion.idParticipante = Participante.id
        db.session.commit()
        flash('success')
        flash('Se ha asignado un nuevo responsable a la acción') 
        return redirect(url_for('acciones.vistaListaAccionesSinAsignar'))

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

@acciones.route('/modificar-estado-accionG/<string:idAccion>')
def vistaModificacionEstadoAccion(idAccion):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    accion = Accion.query.filter_by(idAccion = idAccion).first()
    return render_template('acciones/editarEstadoG.html', usuario=usuario, accion=accion)

@acciones.route('/actualizar-estado-accionG', methods=['POST'])
def actualizarEstadoAccion():
    if request.method == 'POST':
        idAccion = request.form['idaccion']
        accion = Accion.query.filter_by(idAccion = idAccion).first()
        estado = request.form['estado']
        if estado == 'Iniciado':
            accion.porcentaje = 0.0
            accion.estado = estado
            accion.detalles = ''
        elif estado == 'En Proceso':
            accion.porcentaje = float(request.form['porcentaje'])
            accion.estado = estado
        elif estado == 'En Revisión':
            accion.estado = estado
            accion.detalles = request.form['detalles']
        elif estado == 'Pospuesto':
            accion.estado = estado
            accion.detalles = request.form['detalles']
        elif estado == 'Cancelado':
            accion.estado = estado
            accion.detalles = request.form['detalles']
        elif estado == 'Finalizado':
            accion.porcentaje = 100.00
            accion.estado = estado
            accion.detalles = request.form['detalles']
        db.session.commit()
        flash('success')
        flash('El estado de la acción ha sido actualizada correctamente')
        return redirect(url_for('acciones.vistaListaAcciones'))