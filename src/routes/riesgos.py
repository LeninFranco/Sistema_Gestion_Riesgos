from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.activos import Activo
from src.models.riesgo import Riesgo
from src.models.tipo_riesgo import TipoRiesgo

riesgos = Blueprint('riesgos', __name__)

def definirUmbral(factor: float) -> str:
    if factor > 0 and factor < 3:
        return "Bajo"
    if factor >= 3 and factor < 6:
        return "Medio"
    if factor >= 6 and factor <= 9:
        return "Alto"

umbrales = {
    'Probabilidad': {
        'Bajo': "La probabilidad de explotación exitosa de la vulnerabilidad es mínima o poco probable. Los factores de amenaza y vulnerabilidad indican que se requerirían condiciones extremadamente excepcionales para que un ataque tenga éxito en el contexto del proyecto.",
        'Medio': "Sugiere que la probabilidad de explotación exitosa de la vulnerabilidad es moderada. Los factores de amenaza y vulnerabilidad indican una posibilidad razonable de un ataque exitoso en el contexto del proyecto.",
        'Alto': "Indica que la probabilidad de explotación exitosa de la vulnerabilidad es alta o muy probable. Los factores de amenaza y vulnerabilidad sugieren que es probable que ocurra un ataque exitoso con relativa frecuencia en el contexto del proyecto."
    },
    'Impacto': {
        'Bajo': "Refleja que el impacto resultante de un incidente de seguridad es mínimo o tiene un efecto limitado en los activos y el proyecto en sí. Los valores de sensibilidad del activo e impacto empresarial indican un impacto bajo en el contexto del proyecto.",
        'Medio': "Indica que el impacto de un incidente de seguridad es moderado y puede tener un efecto significativo en ciertos aspectos del proyecto. Los valores de sensibilidad del activo e impacto empresarial sugieren un impacto de nivel medio en el contexto del proyecto.",
        'Alto': "Señala que el impacto de un incidente de seguridad es alto y puede tener consecuencias graves en los activos y el proyecto en general. Los valores de sensibilidad del activo e impacto empresarial indican un impacto alto en el contexto del proyecto."
    },
    'Umbral Total': {
        'Insignificante': "Significa que el riesgo resultante es prácticamente nulo o de poca importancia en el contexto del proyecto. La probabilidad e el impacto combinados no representan una amenaza significativa para el proyecto y no justifican acciones inmediatas.",
        'Bajo': "Indica que el riesgo es manejable y no representa una amenaza crítica en el contexto del proyecto. La combinación de probabilidad e impacto sugiere un riesgo bajo que puede abordarse en un momento oportuno.",
        'Medio': "Señala un riesgo significativo que requiere atención y gestión activa en el contexto del proyecto. La combinación de probabilidad e impacto sugiere un riesgo de nivel medio que debe ser monitoreado y mitigado.",
        'Alto': "Refleja un riesgo sustancial que requiere una acción inmediata y enérgica en el contexto del proyecto. La probabilidad y el impacto combinados indican un riesgo alto que debe abordarse de manera prioritaria.",
        'Crítico': "Indica un riesgo extremadamente grave y urgente que podría tener consecuencias catastróficas para el proyecto. La combinación de probabilidad e impacto sugiere un riesgo crítico que requiere una respuesta inmediata y exhaustiva."
    }
}


factores_de_amenaza = {
    'nivel_de_habilidad': {
        1: "Sin habilidades técnicas: el grupo de amenazas carece de habilidades técnicas.",
        2: "Habilidades técnicas mínimas: habilidades técnicas muy limitadas.",
        3: "Algunas habilidades técnicas: el grupo de amenazas tiene conocimientos técnicos básicos.",
        4: "Usuario avanzado de computadoras: habilidades de usuario avanzado de computadoras.",
        5: "Habilidades de programación y redes: conocimientos sólidos en programación y redes.",
        6: "Habilidades de penetración de seguridad: altamente competentes en penetración de seguridad.",
        7: "Habilidades de élite: expertos altamente especializados en penetración de seguridad.",
        8: "Máximo nivel de habilidad: maestría en penetración de seguridad.",
        9: "Expertos supremos: los atacantes son los mejores en su campo."
    },
    'motivación': {
        1: "Recompensa baja o nula: motivación mínima para atacar.",
        2: "Motivación limitada: baja recompensa como incentivo.",
        3: "Motivación moderada: recompensa potencial como incentivo.",
        4: "Posible recompensa: recompensa significativa como incentivo.",
        5: "Recompensa alta: recompensa sustancial como incentivo.",
        6: "Motivación extrema: fuerte deseo de éxito en el ataque.",
        7: "Motivación excepcional: altamente motivados por la recompensa.",
        8: "Motivación extrema: dispuestos a asumir riesgos significativos.",
        9: "Motivación máxima: fanáticos en busca de la recompensa."
    },
    'oportunidad': {
        1: "Se requiere acceso completo o recursos costosos: acceso extremadamente limitado.",
        2: "Se requiere acceso o recursos especiales: acceso o recursos especiales necesarios.",
        3: "Se requiere algún acceso o recursos: acceso o recursos requeridos.",
        4: "Acceso o recursos especiales útiles: acceso o recursos útiles, pero no esenciales.",
        5: "Amplio acceso y recursos disponibles: acceso y recursos fácilmente disponibles.",
        6: "Acceso y recursos prácticamente ilimitados: acceso y recursos abundantes.",
        7: "Recursos y oportunidades excepcionales: recursos y oportunidades sobresalientes.",
        8: "Recursos y oportunidades extremadamente altos: recursos y oportunidades excepcionales.",
        9: "Amplio y constante acceso a recursos y oportunidades: acceso constante a recursos y oportunidades sin restricciones."
    },
    'tamaño': {
        1: "Desarrolladores: un grupo de amenazas muy pequeño (desarrolladores).",
        2: "Administradores de sistemas: un grupo pequeño (administradores de sistemas).",
        3: "Usuarios de intranet: un grupo de tamaño moderado (usuarios de intranet).",
        4: "Socios: un grupo de tamaño moderado (socios).",
        5: "Usuarios autenticados: un grupo moderado (usuarios autenticados).",
        6: "Usuarios anónimos de Internet: un grupo grande (usuarios anónimos de Internet).",
        7: "Infiltración generalizada: un grupo extremadamente grande.",
        8: "Infiltración masiva: un grupo masivo y altamente coordinado.",
        9: "Infiltración a gran escala: un grupo extremadamente masivo y altamente organizado."
    }
}

factores_de_vulnerabilidad = {
    'facilidad_de_descubrimiento': {
        1: "Prácticamente imposible de descubrir incluso para expertos.",
        2: "Extremadamente difícil de descubrir: muy rara vez detectado.",
        3: "Difícil de descubrir: raramente detectado.",
        4: "Moderadamente difícil de descubrir: ocasionalmente detectado.",
        5: "Relativamente fácil de descubrir: a menudo detectado.",
        6: "Fácil de descubrir: detectado con regularidad.",
        7: "Muy fácil de descubrir: detectado con frecuencia.",
        8: "Altamente detectable: casi siempre descubierto.",
        9: "Herramientas automatizadas disponibles: ampliamente conocido y constantemente detectado."
    },
    'facilidad_de_explotación': {
        1: "Teóricamente posible pero casi impracticable: extremadamente difícil de explotar.",
        2: "Difícil de explotar: raramente explotado con éxito.",
        3: "Moderadamente difícil de explotar: ocasionalmente explotado con éxito.",
        4: "Relativamente fácil de explotar: a menudo explotado con éxito.",
        5: "Fácil de explotar: explotado con regularidad.",
        6: "Muy fácil de explotar: explotado con frecuencia.",
        7: "Extremadamente fácil de explotar: ampliamente conocido y explotado sin esfuerzo.",
        8: "Herramientas automatizadas disponibles: ampliamente conocido y explotado con herramientas automatizadas.",
        9: "Herramientas automatizadas disponibles: ampliamente conocido y explotado con herramientas automatizadas."
    },
    'conciencia': {
        1: "Desconocido: la vulnerabilidad es prácticamente desconocida por los atacantes.",
        2: "Poco conocido: la vulnerabilidad es poco conocida por los atacantes.",
        3: "Moderadamente conocido: la vulnerabilidad es moderadamente conocida por los atacantes.",
        4: "Relativamente conocido: la vulnerabilidad es relativamente conocida por los atacantes.",
        5: "Ampliamente conocido: la vulnerabilidad es ampliamente conocida por los atacantes.",
        6: "Bien conocido: la vulnerabilidad es bien conocida y reconocida por los atacantes.",
        7: "Muy conocido: la vulnerabilidad es muy conocida y todos los atacantes están al tanto.",
        8: "Extremadamente conocido: la vulnerabilidad es extremadamente conocida y es una amenaza constante.",
        9: "Excepcionalmente conocido: la vulnerabilidad es excepcionalmente conocida y es una amenaza constante y grave."
    },
    'detección_de_intrusiones': {
        1: "Detección altamente eficiente: la explotación es muy improbable de detectar.",
        2: "Detección eficiente: la explotación es poco probable de detectar.",
        3: "Detección moderada: la explotación tiene una probabilidad moderada de ser detectada.",
        4: "Detección limitada: la explotación es relativamente probable de ser detectada.",
        5: "Detección promedio: la explotación es probable de ser detectada.",
        6: "Detección moderadamente baja: la explotación es bastante probable de ser detectada.",
        7: "Detección baja: la explotación es muy probable de ser detectada.",
        8: "Detección muy baja: la explotación es extremadamente probable de ser detectada.",
        9: "Detección mínima: la explotación es casi segura de ser detectada."
    }
}

factores_de_impacto_empresarial = {
    'daño_financiero': {
        1: "Menos que el costo de solucionar la vulnerabilidad: el daño financiero es mínimo.",
        2: "Costo de solucionar supera el daño: el daño financiero es bajo.",
        3: "Efecto menor en la ganancia anual: el daño financiero es moderado.",
        4: "Efecto significativo en la ganancia anual: el daño financiero es considerable.",
        5: "Daño financiero alto: el daño financiero es significativo.",
        6: "Daño financiero muy alto: el daño financiero es alto.",
        7: "Daño financiero extremadamente alto: el daño financiero es muy alto.",
        8: "Daño financiero máximo: el daño financiero es extremadamente alto.",
        9: "Quiebra: el daño financiero es máximo, lo que puede llevar a la quiebra."
    },
    'daño_a_la_reputación': {
        1: "Daño mínimo: el daño a la reputación es mínimo.",
        2: "Daño menor a la reputación: el daño a la reputación es bajo.",
        3: "Pérdida de cuentas importantes: el daño a la reputación afecta la pérdida de cuentas importantes.",
        4: "Pérdida de fondo de comercio: el daño a la reputación afecta el fondo de comercio.",
        5: "Daño de marca: el daño a la reputación afecta significativamente la marca.",
        6: "Daño de marca grave: el daño a la reputación es alto y afecta gravemente la marca.",
        7: "Daño de marca extremo: el daño a la reputación es extremadamente alto y afecta de manera extrema la marca.",
        8: "Daño de marca catastrófico: el daño a la reputación es catastrófico para la marca.",
        9: "Daño de marca irreparable: el daño a la reputación es irreparable y potencialmente fatal para la marca."
    },
    'incumplimiento': {
        1: "Infracción menor: el incumplimiento resultante es menor y no representa una amenaza significativa.",
        2: "Infracción clara: el incumplimiento resultante es claro pero no es de alto perfil.",
        3: "Infracción de alto perfil: el incumplimiento resultante es de alto perfil y atraerá atención significativa.",
        4: "Infracción grave: el incumplimiento resultante es grave y puede tener consecuencias legales significativas.",
        5: "Infracción extremadamente grave: el incumplimiento resultante es extremadamente grave y conlleva graves consecuencias legales.",
        6: "Infracción catastrófica: el incumplimiento resultante es catastrófico y puede tener consecuencias legales devastadoras.",
        7: "Infracción potencialmente fatal: el incumplimiento resultante es potencialmente fatal para la organización.",
        8: "Infracción crítica: el incumplimiento resultante es crítico y amenaza gravemente la supervivencia de la organización.",
        9: "Infracción catastrófica: el incumplimiento resultante es catastrófico y puede llevar a la organización a la quiebra."
    },
    'violación_de_la_privacidad': {
        1: "Divulgación de información personal mínima: solo se expone información personal de un individuo.",
        2: "Divulgación de información personal limitada: se expone información personal de un pequeño grupo de personas.",
        3: "Divulgación de información personal moderada: se expone información personal de cientos de personas.",
        4: "Divulgación de información personal considerable: se expone información personal de miles de personas.",
        5: "Divulgación de información personal significativa: se expone información personal de millones de personas.",
        6: "Divulgación de información personal alta: se expone información personal de una gran cantidad de personas.",
        7: "Divulgación de información personal muy alta: se expone información personal de muchas personas.",
        8: "Divulgación de información personal extremadamente alta: se expone información personal de una cantidad masiva de personas.",
        9: "Divulgación de información personal máxima: se expone información personal de un número excepcionalmente grande de personas."
    }
}

@riesgos.route('/listar-riesgos')
def vistaListaRiesgos():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    riesgos = []
    for activo in activos:
        riesgos += activo.riesgos
    riesgos_umbrales = []
    for riesgo in riesgos:
        riesgos_umbrales.append((riesgo, definirUmbral(riesgo.probabilidad), definirUmbral(riesgo.impacto)))
    return render_template('riesgos/listaRiesgos.html', usuario=usuario, riesgos_umbrales=riesgos_umbrales, umbrales=umbrales, tiposRiesgo=TipoRiesgo.query.all(), activos=proyecto.activos, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad)

@riesgos.route('/modificar-riesgo/<string:idRiesgo>')
def vistaModificacionRiesgo(idRiesgo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    riesgo = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
    return render_template('riesgos/edicionRiesgo.html', usuario=usuario, riesgo=riesgo, tiposRiesgo=TipoRiesgo.query.all(), activos=proyecto.activos, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad)

@riesgos.route('/anadir-riesgo', methods=['POST'])
def añadirRiesgo():
    if request.method == 'POST':
        clave = request.form['clave']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        amenaza = request.form['amenaza']
        nivelHabilidad = request.form['nivelHabilidad']
        motivacion = request.form['motivacion']
        oportunidad = request.form['oportunidad']
        tamaño = request.form['tamaño']
        vulnerabilidad = request.form['vulnerabilidad']
        facilidadDescubrimiento = request.form['facilidadDescubrimiento']
        facilidadExplotacion = request.form['facilidadExplotacion']
        conciencia = request.form['conciencia']
        deteccionIntrusiones = request.form['deteccionIntrusiones']
        impactoFinanciero = request.form['impactoFinanciero']
        impactoReputacion = request.form['impactoReputacion']
        impactoLegal = request.form['impactoLegal']
        impactoUsuarios = request.form['impactoUsuarios']
        idTipoRiesgo = request.form['idTipoRiesgo']
        idActivo = request.form['idActivo']
        r = Riesgo(
            clave=clave,
            nombre=nombre,
            descripcion=descripcion,
            amenaza=amenaza,
            nivelHabilidad=int(nivelHabilidad),
            motivacion=int(motivacion),
            oportunidad=int(oportunidad),
            tamaño=int(tamaño),
            vulnerabilidad=vulnerabilidad,
            facilidadDescubrimiento=int(facilidadDescubrimiento),
            facilidadExplotacion=int(facilidadExplotacion),
            conciencia=int(conciencia),
            deteccionIntrusiones=int(deteccionIntrusiones),
            impactoFinanciero=int(impactoFinanciero),
            impactoReputacion=int(impactoReputacion),
            impactoLegal=int(impactoLegal),
            impactoUsuarios=int(impactoUsuarios),
            idTipoRiesgo=idTipoRiesgo,
            idActivo=idActivo
        )
        activo = Activo.query.filter_by(idActivo=idActivo).first()
        r.priorizarRiesgo(activo.sensibilidad)
        db.session.add(r)
        db.session.commit()
        flash('success')
        flash('El riesgo ha sido añadido correctamente')
        return redirect(url_for('riesgos.vistaListaRiesgos'))

@riesgos.route('/actualizar-riesgo', methods=['POST'])
def actualizarRiesgo():
    if request.method == 'POST':
        idRiesgo = request.form['idRiesgo']
        clave = request.form['clave']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        amenaza = request.form['amenaza']
        nivelHabilidad = request.form['nivelHabilidad']
        motivacion = request.form['motivacion']
        oportunidad = request.form['oportunidad']
        tamaño = request.form['tamaño']
        vulnerabilidad = request.form['vulnerabilidad']
        facilidadDescubrimiento = request.form['facilidadDescubrimiento']
        facilidadExplotacion = request.form['facilidadExplotacion']
        conciencia = request.form['conciencia']
        deteccionIntrusiones = request.form['deteccionIntrusiones']
        impactoFinanciero = request.form['impactoFinanciero']
        impactoReputacion = request.form['impactoReputacion']
        impactoLegal = request.form['impactoLegal']
        impactoUsuarios = request.form['impactoUsuarios']
        idTipoRiesgo = request.form['idTipoRiesgo']
        idActivo = request.form['idActivo']
        r = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
        r.clave=clave
        r.nombre=nombre
        r.descripcion=descripcion
        r.amenaza=amenaza
        r.nivelHabilidad=int(nivelHabilidad)
        r.motivacion=int(motivacion)
        r.oportunidad=int(oportunidad)
        r.tamaño=int(tamaño)
        r.vulnerabilidad=vulnerabilidad
        r.facilidadDescubrimiento=int(facilidadDescubrimiento)
        r.facilidadExplotacion=int(facilidadExplotacion)
        r.conciencia=int(conciencia)
        r.deteccionIntrusiones=int(deteccionIntrusiones)
        r.impactoFinanciero=int(impactoFinanciero)
        r.impactoReputacion=int(impactoReputacion)
        r.impactoLegal=int(impactoLegal)
        r.impactoUsuarios=int(impactoUsuarios)
        r.idTipoRiesgo=idTipoRiesgo
        r.idActivo=idActivo
        activo = Activo.query.filter_by(idActivo=idActivo).first()
        r.priorizarRiesgo(activo.sensibilidad)
        db.session.commit()
        flash('success')
        flash('El riesgo ha sido actualizado correctamente')
        return redirect(url_for('riesgos.vistaListaRiesgos'))

@riesgos.route('/eliminar-riesgo/<string:idRiesgo>')
def eliminarRiesgo(idRiesgo):
    r = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
    db.session.delete(r)
    db.session.commit()
    flash('danger')
    flash('El riesgo fue eliminado exitosamente') 
    return redirect(url_for('riesgos.vistaListaRiesgos'))