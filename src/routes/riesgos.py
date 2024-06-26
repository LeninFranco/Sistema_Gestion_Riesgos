from flask import Blueprint, session, redirect, url_for, render_template, request, flash, jsonify
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from src.models.activos import Activo
from src.models.riesgo import Riesgo
from src.models.activos_riesgos import ActivosRiesgos
from src.models.historialRiesgos import HistorialRiesgo
from src.models.historialActivos import HistorialActivo
from datetime import datetime
import re

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

#
# Listas para activos
#

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

tiposRiesgo = [
    'Físico',
    'Lógico',
    'Organizacional'
]

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

estatus = [
    'En uso',
    'Desuso'
]

agentes_amenaza = [
    'Hackers',
    'Ciberdelincuentes',
    'Estado-Nación',
    'Empleados Descontentos o Desleales',
    'Activistas Cibernéticos',
    'Competidores Comerciales',
    'Usuarios Malintencionados Internos',
    'Bots y Botnets',
    'Grupos de Crimen Organizado',
    'Agentes Ambientales',
    'Agentes Externos a la Organización',
    'Errores Humanos del Personal',
    'Fallas Informáticas'
]


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
        dictRiesgos[clave]['activos'] = sorted(dictRiesgos[clave]['activos'], key=lambda a: a[4], reverse=True)
    
    claveSig = f'{proyecto.clave}:R-{str(len(dictRiesgos.keys())+1).zfill(4)}'
    return render_template('riesgos/listaRiesgos.html', usuario=usuario, proyecto=proyecto, claveSig=claveSig, dictRiesgos=dictRiesgos, riesgos=riesgos, riesgos_umbrales=riesgos_umbrales, umbrales=umbrales, tiposRiesgo=tiposRiesgo, tiposActivo=tiposActivo, estatus=estatus, cdi=cdi, frecuencia=frecuencia, activos=proyecto.activos, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad, agentes_amenaza=agentes_amenaza)

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
    return render_template('riesgos/edicionRiesgo.html', usuario=usuario, riesgo=riesgo, tiposRiesgo=tiposRiesgo, activos=riesgo.activos_asociados, tiposActivo=tiposActivo, estatus=estatus, cdi=cdi, frecuencia=frecuencia, activosProyecto=proyecto.activos , factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad, agentes_amenaza=agentes_amenaza)


@riesgos.route('/modificar-nuevo-riesgo/<string:idRiesgo>')
def vistaModificacionRiesgoA(idRiesgo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    riesgo = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
    return render_template('historialRiesgos/actualizarRiesgo.html', usuario=usuario, riesgo=riesgo, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad)

@riesgos.route('/anadir-riesgo', methods=['POST'])
def añadirRiesgo():
    if request.method == 'POST':
        clave = request.form['clave']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        idTipoRiesgo = request.form['idTipoRiesgo']
        nivelHabilidad = request.form['nivelHabilidad']
        amenaza = request.form['amenaza']
        vulnerabilidad = request.form['vulnerabilidad']
        motivacion = request.form['motivacion']
        oportunidad = request.form['oportunidad']
        tamaño = request.form['tamaño']
        facilidadDescubrimiento = request.form['facilidadDescubrimiento']
        facilidadExplotacion = request.form['facilidadExplotacion']
        conciencia = request.form['conciencia']
        deteccionIntrusiones = request.form['deteccionIntrusiones']
        impactoFinanciero = request.form['impactoFinanciero']
        impactoReputacion = request.form['impactoReputacion']
        impactoLegal = request.form['impactoLegal']
        impactoUsuarios = request.form['impactoUsuarios']
        idActivos = request.form.getlist('idActivos')
        
        r = Riesgo(
            clave=clave,
            nombre=nombre,
            descripcion=descripcion,
            tipoRiesgo=idTipoRiesgo,
            nivelHabilidad=int(nivelHabilidad),
            amenaza=amenaza,
            vulnerabilidad=vulnerabilidad,
            motivacion=int(motivacion),
            oportunidad=int(oportunidad),
            tamaño=int(tamaño),
            facilidadDescubrimiento=int(facilidadDescubrimiento),
            facilidadExplotacion=int(facilidadExplotacion),
            conciencia=int(conciencia),
            deteccionIntrusiones=int(deteccionIntrusiones),
            impactoFinanciero=int(impactoFinanciero),
            impactoReputacion=int(impactoReputacion),
            impactoLegal=int(impactoLegal),
            impactoUsuarios=int(impactoUsuarios)
        )
        
        # Obtener activos de formulario
        activos = []
        for idActivo in idActivos:
            activo = Activo.query.filter_by(idActivo=str(idActivo)).first()
            activos.append(activo)
        db.session.add(r)
        db.session.commit()
        
        # Añadir asociaciones por cada activo con el riesgo r
        asociaciones = []
        for activo in activos:
            probabilidadRiesgo = obtenerProbabilidad(r)
            impactoRiesgoActivo = obtenerImpacto(r, activo)
            asociacion = ActivosRiesgos(riesgo = r, activo = activo, probabilidad = probabilidadRiesgo, impacto = impactoRiesgoActivo, total = obtenerTotal(probabilidadRiesgo,impactoRiesgoActivo), umbral = obtenerUmbral(probabilidadRiesgo,impactoRiesgoActivo))
            asociaciones.append(asociacion)
        db.session.add_all(asociaciones)
        db.session.commit()

        dictRiesgos = {}

        for asociacion in r.activos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos:
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,
                    'activos' : [ (asociacion.activo, obtenerProbabilidad(asociacion.riesgo), obtenerImpacto(asociacion.riesgo,asociacion.activo), asociacion.umbral, asociacion.total) ]
                }
            else:
                dictRiesgos[asociacion.riesgo.clave]['activos'].append( (asociacion.activo, obtenerProbabilidad(asociacion.riesgo), obtenerImpacto(asociacion.riesgo,asociacion.activo), asociacion.umbral, asociacion.total) ) #La lista de activos con la que esta asociado el riesgo con sus valores

        for clave in dictRiesgos.keys():
            dictRiesgos[clave]['activos'] = sorted(dictRiesgos[clave]['activos'], key=lambda a: a[4], reverse=True)

        histRisk = HistorialRiesgo(r.nivelHabilidad, r.motivacion, r.oportunidad, r.tamaño, r.facilidadDescubrimiento, r.facilidadExplotacion, r.conciencia, r.deteccionIntrusiones, r.impactoFinanciero, r.impactoReputacion, r.impactoLegal, r.impactoUsuarios, dictRiesgos[r.clave]['activos'][0][1] , dictRiesgos[r.clave]['activos'][0][2], dictRiesgos[r.clave]['activos'][0][4], dictRiesgos[r.clave]['activos'][0][2], 'Primera Evaluación del Riesgos', r.idRiesgo)
        db.session.add(histRisk)
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
        TipoRiesgo = request.form['idTipoRiesgo']
        nivelHabilidad = request.form['nivelHabilidad']
        motivacion = request.form['motivacion']
        oportunidad = request.form['oportunidad']
        amenaza = request.form['amenaza']
        vulnerabilidad = request.form['vulnerabilidad']
        tamaño = request.form['tamaño']
        facilidadDescubrimiento = request.form['facilidadDescubrimiento']
        facilidadExplotacion = request.form['facilidadExplotacion']
        conciencia = request.form['conciencia']
        deteccionIntrusiones = request.form['deteccionIntrusiones']
        impactoFinanciero = request.form['impactoFinanciero']
        impactoReputacion = request.form['impactoReputacion']
        impactoLegal = request.form['impactoLegal']
        impactoUsuarios = request.form['impactoUsuarios']
        r = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()

        r.clave=clave
        r.nombre=nombre
        r.descripcion=descripcion
        r.tipoRiesgo = TipoRiesgo
        r.amenaza = amenaza
        r.vulneravilidad = vulnerabilidad
        r.nivelHabilidad=int(nivelHabilidad)
        r.motivacion=int(motivacion)
        r.oportunidad=int(oportunidad)
        r.tamaño=int(tamaño)
        r.facilidadDescubrimiento=int(facilidadDescubrimiento)
        r.facilidadExplotacion=int(facilidadExplotacion)
        r.conciencia=int(conciencia)
        r.deteccionIntrusiones=int(deteccionIntrusiones)
        r.impactoFinanciero=int(impactoFinanciero)
        r.impactoReputacion=int(impactoReputacion)
        r.impactoLegal=int(impactoLegal)
        r.impactoUsuarios=int(impactoUsuarios)

        for asociacion in r.activos_asociados:
            probabilidadRiesgo = obtenerProbabilidad(r)
            impactoRiesgoActivo = obtenerImpacto(r, asociacion.activo)
            asociacion.probabilidad = probabilidadRiesgo
            asociacion.impacto = impactoRiesgoActivo
            asociacion.total = obtenerTotal(probabilidadRiesgo, impactoRiesgoActivo)
            asociacion.umbral = obtenerUmbral(probabilidadRiesgo,impactoRiesgoActivo)

        db.session.commit()

        flash('success')
        flash('El riesgo ha sido actualizado correctamente')
        return redirect(url_for('riesgos.vistaListaRiesgos'))


@riesgos.route('/actualizar-nuevo-riesgo', methods=['POST'])
def actualizarRiesgoA():
    if request.method == 'POST':
        idRiesgo = request.form['idRiesgo']
        nivelHabilidad = request.form['nivelHabilidad']
        motivacion = request.form['motivacion']
        oportunidad = request.form['oportunidad']
        tamaño = request.form['tamaño']
        facilidadDescubrimiento = request.form['facilidadDescubrimiento']
        facilidadExplotacion = request.form['facilidadExplotacion']
        conciencia = request.form['conciencia']
        deteccionIntrusiones = request.form['deteccionIntrusiones']
        impactoFinanciero = request.form['impactoFinanciero']
        impactoReputacion = request.form['impactoReputacion']
        impactoLegal = request.form['impactoLegal']
        impactoUsuarios = request.form['impactoUsuarios']
        detalles = request.form['detalles']
        r = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()

        r.nivelHabilidad=int(nivelHabilidad)
        r.motivacion=int(motivacion)
        r.oportunidad=int(oportunidad)
        r.tamaño=int(tamaño)
        r.facilidadDescubrimiento=int(facilidadDescubrimiento)
        r.facilidadExplotacion=int(facilidadExplotacion)
        r.conciencia=int(conciencia)
        r.deteccionIntrusiones=int(deteccionIntrusiones)
        r.impactoFinanciero=int(impactoFinanciero)
        r.impactoReputacion=int(impactoReputacion)
        r.impactoLegal=int(impactoLegal)
        r.impactoUsuarios=int(impactoUsuarios)

        dictRiesgos = {}
        for asociacion in r.activos_asociados:
            probabilidadRiesgo = obtenerProbabilidad(r)
            impactoRiesgoActivo = obtenerImpacto(r, asociacion.activo)
            asociacion.probabilidad = probabilidadRiesgo
            asociacion.impacto = impactoRiesgoActivo
            asociacion.total = obtenerTotal(probabilidadRiesgo, impactoRiesgoActivo)
            asociacion.umbral = obtenerUmbral(probabilidadRiesgo,impactoRiesgoActivo)

        db.session.commit()
        
        for asociacion in r.activos_asociados:
            if not asociacion.riesgo.clave in dictRiesgos:
                dictRiesgos[asociacion.riesgo.clave] = {
                    'riesgo' : asociacion.riesgo,
                    'activos' : [ (asociacion.activo, obtenerProbabilidad(asociacion.riesgo), obtenerImpacto(asociacion.riesgo,asociacion.activo), asociacion.umbral, asociacion.total) ]
                }
            else:
                dictRiesgos[asociacion.riesgo.clave]['activos'].append( (asociacion.activo, obtenerProbabilidad(asociacion.riesgo), obtenerImpacto(asociacion.riesgo,asociacion.activo), asociacion.umbral, asociacion.total) ) #La lista de activos con la que esta asociado el riesgo con sus valores

        for clave in dictRiesgos.keys():
            dictRiesgos[clave]['activos'] = sorted(dictRiesgos[clave]['activos'], key=lambda a: a[4], reverse=True)

        histRisk = HistorialRiesgo(r.nivelHabilidad, r.motivacion, r.oportunidad, r.tamaño, r.facilidadDescubrimiento, r.facilidadExplotacion, r.conciencia, r.deteccionIntrusiones, r.impactoFinanciero, r.impactoReputacion, r.impactoLegal, r.impactoUsuarios, dictRiesgos[r.clave]['activos'][0][1] , dictRiesgos[r.clave]['activos'][0][2], dictRiesgos[r.clave]['activos'][0][4], dictRiesgos[r.clave]['activos'][0][3], detalles, r.idRiesgo)
        db.session.add(histRisk)
        db.session.commit()

        flash('success')
        flash('El riesgo ha sido actualizado correctamente')
        return redirect(url_for('acciones.vistaListaAcciones'))

@riesgos.route('/eliminar-riesgo/<string:idRiesgo>')
def eliminarRiesgo(idRiesgo):
    r = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
    db.session.delete(r)
    db.session.commit()
    flash('danger')
    flash('El riesgo fue eliminado exitosamente') 
    return redirect(url_for('riesgos.vistaListaRiesgos'))

@riesgos.route('/listar-activos/<string:idRiesgo>')
def listarActivos(idRiesgo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    riesgo = Riesgo.query.filter_by(idRiesgo = idRiesgo).first()
    asociaciones = []
    #for asociacion in riesgo.activos_asociados:
    #    asociaciones.append(asociacion)
    # Por ahora, a opinión de stakeholders
    activosEnRiesgo = []
    for asociacion in riesgo.activos_asociados:
        activosEnRiesgo.append(asociacion.activo)
    activos_listado = []
    for activo in activos:
        if not activo in activosEnRiesgo:
            activos_listado.append(activo)
    return render_template('riesgos/modificarAsociaciones.html', usuario=usuario, riesgo = riesgo, activos = activos, activos_riesgo=activosEnRiesgo, activos_listado = activos_listado, tiposActivo=tiposActivo, estatus=estatus, cdi=cdi, frecuencia=frecuencia, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad)

@riesgos.route('/desligar-activo/<string:idRiesgo>-<string:idActivo>')
def eliminarActivoRiesgo(idRiesgo, idActivo):
    riesgo = Riesgo.query.filter_by(idRiesgo = idRiesgo).first()
    if not len(riesgo.activos_asociados) < 2:
        activo = Activo.query.filter_by(idActivo = idActivo).first()
        asociacion = ActivosRiesgos.query.filter_by(riesgo = riesgo, activo = activo).first()
        db.session.delete(asociacion)
        db.session.commit()
        flash("success")
        flash("El activo ha sido desligado del riesgo")
    else:
        flash("danger")
        flash("El riesgo debe tener al menos un activo")
    return redirect(url_for('riesgos.listarActivos',idRiesgo = idRiesgo))
    

@riesgos.route('/anadir-activo-en-riesgo-existente/<string:idRiesgo>', methods=['POST'])
def añadirActivoARiesgoExstente(idRiesgo):
    if request.method == 'POST':
        idActivo = request.form['idActivo']
        riesgo = Riesgo.query.filter_by(idRiesgo = idRiesgo).first()
        activo = Activo.query.filter_by(idActivo = idActivo).first()
        probabilidadRiesgo = obtenerProbabilidad(riesgo)
        impactoRiesgoActivo = obtenerImpacto(riesgo, activo)
        asociacion = ActivosRiesgos(riesgo = riesgo, activo = activo, probabilidad = probabilidadRiesgo, impacto = impactoRiesgoActivo, total = obtenerTotal(probabilidadRiesgo,impactoRiesgoActivo), umbral = obtenerUmbral(probabilidadRiesgo,impactoRiesgoActivo))
        db.session.add(asociacion)
        db.session.commit()
        flash("success")
        flash("El activo ha sido añadido al riesgo")
        return redirect(url_for('riesgos.listarActivos',idRiesgo = idRiesgo))

@riesgos.route('/anadir-activos-en-riesgo', methods=['POST'])
def añadirActivoEnRiesgo():
    if request.method == 'POST':
        try:
            clave = request.form['clave']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            propietario = request.form['propietario']
            ubicacion = request.form['ubicacion']
            tipoActivo = request.form['tipo']
            estatus = request.form['estatus']
            frecMantenimiento = request.form['frecM']
            frecRenovacion = request.form['frecR']
            fecha_str = request.form['fecha']
            fechaAdquisicion = datetime.strptime(fecha_str, '%Y-%m-%d')

            confidencialidad = int(request.form['confidencialidad'])
            disponibilidad = int(request.form['disponibilidad'])
            integridad = int(request.form['integridad'])
            
            a = Activo(
                clave=clave,
                nombre=nombre,
                descripcion=descripcion,
                propietario=propietario,
                ubicacion=ubicacion,
                tipoActivo=tipoActivo,
                estatus=estatus,
                frecMantenimiento=frecMantenimiento,
                frecRenovacion=frecRenovacion,
                fechaAdquisicion=fechaAdquisicion.replace(hour=0, minute=0, second=0, microsecond=0),
                idProyecto=session['proyecto_id']
            )
            a.evaluarActivo(confidencialidad, disponibilidad, integridad)
            db.session.add(a)
            histAct = HistorialActivo(confidencialidad, disponibilidad, integridad, a.idActivo)
            db.session.add(histAct)
            db.session.commit()
            return jsonify('Ok')
        except:
            db.session.rollback()
            return jsonify('Existe')
    
@riesgos.route('/matriz-riesgos')
def vistaMatrizRiesgos():
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
        dictRiesgos[clave]['activos'] = sorted(dictRiesgos[clave]['activos'], key=lambda a: a[4], reverse=True)
    
    return render_template('matriz/matriz.html', proyecto=proyecto, usuario=usuario, dictRiesgos=dictRiesgos, riesgos=riesgos, riesgos_umbrales=riesgos_umbrales, umbrales=umbrales, tiposRiesgo=tiposRiesgo, tiposActivo=tiposActivo, estatus=estatus, cdi=cdi, frecuencia=frecuencia, activos=proyecto.activos, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad)

@riesgos.route('/historial-riesgos')
def vistaHistorialRiesgos():
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
        dictRiesgos[clave]['activos'] = sorted(dictRiesgos[clave]['activos'], key=lambda a: a[4], reverse=True)

    return render_template('historialRiesgos/listaRiesgos.html', usuario=usuario, dictRiesgos=dictRiesgos, tiposRiesgo=tiposRiesgo, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad, agentes_amenaza=agentes_amenaza)

@riesgos.route('/historial-riesgos/<string:idRiesgo>')
def vistaHistorialRiesgo(idRiesgo):
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    riesgo = Riesgo.query.filter_by(idRiesgo=idRiesgo).first()
    umbral_actual = ""
    total_mayor = 0
    for asociacion in riesgo.activos_asociados:
        if asociacion.total > total_mayor:
            total_mayor = asociacion.total
            umbral_actual = asociacion.umbral

    detalle_activo = {}

    for historial in riesgo.historial:
        clave = re.findall(r'A-\d{4}', historial.detalles)
        if clave:
            claveA = f'{proyecto.clave}:{clave[0]}'
            activo = Activo.query.filter_by(clave=claveA).first()
            detalle_activo[historial.fecha] = (HistorialActivo.query.filter_by(fecha=historial.fecha, idActivo=activo.idActivo).first(), claveA)

    return render_template('historialRiesgos/detallesRiesgo.html', usuario=usuario, riesgo=riesgo, detalle_activo=detalle_activo, umbral_actual=umbral_actual, factores_de_amenaza=factores_de_amenaza, factores_de_impacto_empresarial=factores_de_impacto_empresarial, factores_de_vulnerabilidad=factores_de_vulnerabilidad, agentes_amenaza=agentes_amenaza)

@riesgos.route('/obtener-activos-json', methods=['POST'])
def obtenerActivosJSON():
    tipo_seleccionado = request.json['tipoActivo']
    activos_filtrados = filtrarTipo(tipo_seleccionado)
    activos_serializados = [activo.to_dict() for activo in activos_filtrados]
    return jsonify(activos=[activo for activo in activos_serializados])

def obtenerTodosActivos():
    if not 'user_id' in session:
        return redirect(url_for('login.vistaLogin'))
    usuario = Usuario.query.filter_by(idUsuario = session['user_id']).first()
    if usuario.rol == 1:
        return redirect(url_for('login.logout'))
    if not 'proyecto_id' in session:
        return redirect(url_for('proyectos.vistaListaProyectos'))
    proyecto = Proyecto.query.filter_by(idProyecto = session['proyecto_id']).first()
    activos = proyecto.activos
    return activos

def filtrarTipo(tipo):
    # Lógica para filtrar los activos de la base de datos por tipo
    activosFiltrados = []
    for activo in obtenerTodosActivos():
        if activo.tipoActivo == tipo and activo.estatus == 'En uso':
            activosFiltrados.append(activo)
    return activosFiltrados


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