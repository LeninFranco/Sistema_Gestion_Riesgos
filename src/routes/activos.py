from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.activos import Activo
from src.models.activos_riesgos import ActivosRiesgos
from datetime import datetime

activos = Blueprint('activos', __name__)

cdi = {
    'confidencialidad': {
        0: 'No evaluado.',
        1: "El activo no posee información confidencial y puede ser compartido públicamente sin preocupaciones.",
        2: "El activo tiene información de baja confidencialidad y puede ser compartido con personas de confianza.",
        3: "El activo presenta cierto grado de confidencialidad en la información que posee y debe ser compartido únicamente con personas autorizadas.",
        4: "El activo cuenta con un alto nivel de confidencialidad en la información que posee y solo debe ser compartido con un grupo selecto de personas o departamentos.",
        5: "El activo es sumamente confidencial en la información que tiene y solo puede ser accesible por un número muy limitado de personas con necesidad de saber.",
        6: "El activo requiere una confidencialidad muy alta y solo debe compartirse con individuos altamente autorizados.",
        7: "La información en el activo es altamente sensible y solo puede ser compartida con un pequeño grupo de personas clave.",
        8: "El activo alberga información de máxima importancia y su confidencialidad es crítica, solo permitiendo el acceso a un puñado de individuos de confianza.",
        9: "El activo contiene información extremadamente confidencial y solo puede ser accesible por una persona o entidad absolutamente autorizada."
    },
    'disponibilidad': {
        0: 'No evaluado.',
        1: "La información que maneja el activo está prácticamente siempre inaccesible o inutilizable para la mayoría del personal.",
        2: "La información que maneja el activo posee una disponibilidad limitada y puede volverse inaccesible en momentos críticos.",
        3: "La información que maneja el activo generalmente se encuentra disponible, pero pueden surgir interrupciones ocasionales.",
        4: "La información que maneja el activo cuenta con una alta disponibilidad y se puede acceder en la mayoría de los casos.",
        5: "La información que maneja el activo está siempre disponible sin experimentar interrupciones significativas.",
        6: "La disponibilidad del activo es crítica y debe mantenerse constantemente para respaldar las operaciones.",
        7: "El activo debe estar siempre disponible para garantizar la continuidad de las operaciones y evitar interrupciones críticas.",
        8: "La disponibilidad del activo es esencial y se requieren medidas excepcionales para garantizar un acceso continuo.",
        9: "La disponibilidad del activo es de suprema importancia, y cualquier interrupción puede tener consecuencias graves en las operaciones."
    },
    'integridad': {
        0: 'No evaluado.',
        1: "La información del activo es altamente propensa a la corrupción y a modificaciones no autorizadas.",
        2: "La información del activo tiene un nivel limitado de integridad y puede ser susceptible a cambios no autorizados en ciertas circunstancias.",
        3: "La información del activo es generalmente íntegro, pero pueden ocurrir cambios no autorizados en circunstancias excepcionales.",
        4: "La información del activo es altamente íntegro y es poco probable que se modifique no autorizadamente.",
        5: "La información del activo es extremadamente íntegro y se protege rigurosamente contra cualquier modificación no autorizada.",
        6: "La integridad de la información es crítica y cualquier modificación no autorizada debe ser prevenida a toda costa.",
        7: "El activo alberga información esencial y su integridad es de máxima importancia, asegurando que no se produzcan cambios no autorizados.",
        8: "La integridad de la información en el activo es esencial y debe protegerse con medidas de seguridad rigurosas.",
        9: "La integridad del activo es de suprema importancia y cualquier modificación no autorizada es inaceptable."
    },
    'sensibilidad': {
        0: 'No evaluado.',
        3: "Los activos son relativamente menos críticos en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo moderado en el proyecto.",
        4: "Los activos son relativamente menos críticos en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo moderado en el proyecto.",
        5: "Los activos son relativamente menos críticos en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo moderado en el proyecto.",
        6: "Los activos son relativamente menos críticos en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo moderado en el proyecto.",
        7: "Los activos son relativamente menos críticos en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo moderado en el proyecto.",
        8: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, aunque no tan severo como en niveles más altos.",
        9: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, aunque no tan severo como en niveles más altos.",
        10: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, aunque no tan severo como en niveles más altos.",
        11: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, aunque no tan severo como en niveles más altos.",
        12: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, aunque no tan severo como en niveles más altos.",
        13: "Los activos son de importancia moderada en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo considerable en el proyecto.",
        14: "Los activos son de importancia moderada en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo considerable en el proyecto.",
        15: "Los activos son de importancia moderada en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo considerable en el proyecto.",
        16: "Los activos son de importancia moderada en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo considerable en el proyecto.",
        17: "Los activos son de importancia moderada en términos de seguridad de la información. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo considerable en el proyecto.",
        18: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, y se requiere una atención inmediata para mitigar sus riesgos.",
        19: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, y se requiere una atención inmediata para mitigar sus riesgos.",
        20: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, y se requiere una atención inmediata para mitigar sus riesgos.",
        21: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, y se requiere una atención inmediata para mitigar sus riesgos.",
        22: "Los activos con esta sensibilidad son importantes para la organización. La pérdida de confidencialidad, integridad o disponibilidad de estos activos tendría un impacto negativo, y se requiere una atención inmediata para mitigar sus riesgos.",
        23: "Los activos con esta sensibilidad son críticos para la organización. La pérdida de confidencialidad, integridad o disponibilidad sería catastrófica, y se requiere atención inmediata y medidas extremas para mitigar sus riesgos.",
        24: "Los activos con esta sensibilidad son críticos para la organización. La pérdida de confidencialidad, integridad o disponibilidad sería catastrófica, y se requiere atención inmediata y medidas extremas para mitigar sus riesgos.",
        25: "Los activos con esta sensibilidad son críticos para la organización. La pérdida de confidencialidad, integridad o disponibilidad sería catastrófica, y se requiere atención inmediata y medidas extremas para mitigar sus riesgos.",
        26: "Los activos con esta sensibilidad son críticos para la organización. La pérdida de confidencialidad, integridad o disponibilidad sería catastrófica, y se requiere atención inmediata y medidas extremas para mitigar sus riesgos.",
        27: "Los activos con esta sensibilidad son críticos para la organización. La pérdida de confidencialidad, integridad o disponibilidad sería catastrófica, y se requiere atención inmediata y medidas extremas para mitigar sus riesgos."
    }
}

tiposActivo = [
    'Información/Documentos',
    'Aplicaciones',
    'Plataformas',
    'Bases de Datos',
    'Red/Telecomunicaciones',
    'Intangibles',
    'Gente/Personal',
    'Físico'
]

frecuencia = [
    'No Requiere',
    'Diario',
    'Semanal',
    'Quincenal',
    'Mensual',
    'Bimestral',
    'Trimestral',
    'Semestral',
    'Anual'
]

@activos.route('/listar-inventario')
def vistaListaActivos():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    return render_template('activos/listaActivosI.html', usuario=usuario, activos=activos, frecuencia=frecuencia, tiposActivo=tiposActivo)

@activos.route('/modificar-activo/<string:idActivo>')
def vistaModificacionActivos(idActivo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    activo = Activo.query.filter_by(idActivo=idActivo).first()
    return render_template('activos/edicionActivos.html', usuario=usuario, activo=activo, frecuencia=frecuencia, tiposActivo=tiposActivo)

@activos.route('/anadir-activos', methods=['POST'])
def añadirActivos():
    if request.method == 'POST':
        try:
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            propietario = request.form['propietario']
            ubicacion = request.form['ubicacion']
            tipoActivo = request.form['tipo']
            frecMantenimiento = request.form['frecM']
            frecRenovacion = request.form['frecR']
            fecha_str = request.form['fecha']
            fechaAdquisicion = datetime.strptime(fecha_str, '%Y-%m-%d')

            a = Activo(
                clave=clave,
                nombre=nombre,
                descripcion=descripcion,
                propietario=propietario,
                ubicacion=ubicacion,
                tipoActivo=tipoActivo,
                frecMantenimiento=frecMantenimiento,
                frecRenovacion=frecRenovacion,
                fechaAdquisicion=fechaAdquisicion.replace(hour=0, minute=0, second=0, microsecond=0),
                idProyecto=session['proyecto_id']
            )
            db.session.add(a)
            db.session.commit()
            flash('success')
            flash('El activo ha sido añadido correctamente')
        except:
            db.session.rollback()
            flash('danger')
            flash('La clave del activo ya existe')
        return redirect(url_for('activos.vistaListaActivos'))

@activos.route('/actualizar-activos', methods=['POST'])
def modificarActivos():
    if request.method == 'POST':
        try:
            idActivo = request.form['idactivo']
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            propietario = request.form['propietario']
            ubicacion = request.form['ubicacion']
            tipoActivo = request.form['tipo']
            frecMantenimiento = request.form['frecM']
            frecRenovacion = request.form['frecR']
            fecha_str = request.form['fecha']
            fechaAdquisicion = datetime.strptime(fecha_str, '%Y-%m-%d')
            a = Activo.query.filter_by(idActivo=idActivo).first()
            a.clave = clave
            a.nombre=nombre
            a.descripcion=descripcion
            a.propietario = propietario
            a.ubicacion = ubicacion
            a.tipoActivo = tipoActivo
            a.frecMantenimiento = frecMantenimiento
            a.frecRenovacion = frecRenovacion
            a.fechaAdquisicion = fechaAdquisicion
            db.session.commit()
            flash('success')
            flash('El activo ha sido modificado correctamente')
        except:
            db.session.rollback()
            flash('danger')
            flash('La clave del activo ya existe')
        return redirect(url_for('activos.vistaListaActivos'))

@activos.route('/listar-evaluaciones')
def vistaListaEvaluaciones():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    return render_template('activos/listaActivosE.html', usuario=usuario, activos=activos, cdi=cdi)

@activos.route('/evaluar-activo/<string:idActivo>')
def vistaEvaluacionActivos(idActivo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    activo = Activo.query.filter_by(idActivo=idActivo).first()
    return render_template('activos/evaluacionActivo.html', usuario=usuario, activo=activo, cdi=cdi);

@activos.route('/evaluando-activos', methods=['POST'])
def evaluacionActivos():
    if request.method == 'POST':
        idActivo = request.form['idactivo']
        confidencialidad = int(request.form['confidencialidad'])
        disponibilidad = int(request.form['disponibilidad'])
        integridad = int(request.form['integridad'])
        a = Activo.query.filter_by(idActivo=idActivo).first()
        a.evaluarActivo(confidencialidad, disponibilidad, integridad)
        db.session.commit()
        flash('success')
        flash('El activo ha sido evaluado correctamente')
        return redirect(url_for('activos.vistaListaEvaluaciones'))