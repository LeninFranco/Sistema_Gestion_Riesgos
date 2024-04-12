from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.responsables import Participantes
from src.models.acciones import Accion
from src.models.historialAcciones import HistorialAccion
from src.utils.db import db
from datetime import datetime

accionesP = Blueprint('accionesP', __name__)

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

@accionesP.route('/lista-accionesP')
def vistaListaAccionesP():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectosP.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    asociacion = Participantes.query.filter_by(idUsuario=usuario.idUsuario, idProyecto=proyecto.idProyecto).first()
    acciones_finalizadas_canceladas = []
    otras_acciones = []
    for accion in asociacion.acciones:
        if accion.estado in ['Finalizado', 'Cancelado']:
            acciones_finalizadas_canceladas.append(accion)
        else:
            otras_acciones.append(accion)
    otras_acciones_ordenadas = sorted(otras_acciones, key=lambda x: abs((datetime.now() - datetime.combine(x.fechaFin, datetime.min.time())).total_seconds()))
    acciones_ordenadas = otras_acciones_ordenadas + acciones_finalizadas_canceladas
    return render_template('vistas_participantes/listaAccionesP.html', usuario=usuario, proyecto=proyecto, acciones=acciones_ordenadas, controlesISO27001 = controlesISO27001,categoriasISO27001 = categoriasISO27001)

@accionesP.route('/modificar-estado-accion/<string:idAccion>')
def vistaModificacionEstadoAccion(idAccion):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 0:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectosP.vistaListaProyectos'))
    accion = Accion.query.filter_by(idAccion = idAccion).first()
    return render_template('vistas_participantes/editarEstado.html', usuario=usuario, accion=accion)

@accionesP.route('/actualizar-estado-accion', methods=['POST'])
def actualizarEstadoAccion():
    if request.method == 'POST':
        idAccion = request.form['idaccion']
        accion = Accion.query.filter_by(idAccion = idAccion).first()
        estado = request.form['estado']
        if estado == 'En Proceso':
            accion.porcentaje = float(request.form['porcentaje'])
            accion.estado = estado
            accion.detalles = request.form['detalles']
        elif estado == 'Cancelado':
            accion.estado = estado
            accion.detalles = request.form['detalles']
        elif estado == 'Finalizado':
            accion.porcentaje = 100.00
            accion.estado = estado
            accion.detalles = request.form['detalles']
        autor = Usuario.query.filter_by(idUsuario=session['user_id']).first()
        histAcc = HistorialAccion(accion.porcentaje, accion.estado, accion.detalles, f'{autor.nombre} {autor.apellidoPaterno} {autor.apellidoMaterno} - {autor.departamento}', accion.idAccion)
        db.session.add(histAcc)
        db.session.commit()
        flash('success')
        flash('El estado de la acción ha sido actualizada correctamente')
        return redirect(url_for('accionesP.vistaListaAccionesP'))
