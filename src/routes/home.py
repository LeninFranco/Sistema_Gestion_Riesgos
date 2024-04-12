from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from src.utils.db import db
from src.models.usuarios import Usuario
from src.models.proyectos import Proyecto
from datetime import datetime

home = Blueprint('home', __name__)

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

@home.route('/home')
def vistaHome():
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

    grafica = (['Insignificante', 'Bajo', 'Medio', 'Alto', 'Crítico'], [0,0,0,0,0])
    for clave in dictRiesgos.keys():
        if dictRiesgos[clave]['activos'][0][3] == 'Insignificante':
            grafica[1][0] += 1
        elif dictRiesgos[clave]['activos'][0][3] == 'Bajo':
            grafica[1][1] += 1
        elif dictRiesgos[clave]['activos'][0][3] == 'Medio':
            grafica[1][2] += 1
        elif dictRiesgos[clave]['activos'][0][3] == 'Alto':
            grafica[1][3] += 1
        else:
            grafica[1][4] += 1
    
    nivel_riesgo_valor = {'Insignificante': 0, 'Bajo': 1, 'Medio': 2, 'Alto': 3, 'Crítico': 4}

    top_10_riesgos = sorted(dictRiesgos.values(), key=lambda x: (nivel_riesgo_valor[x['activos'][0][3]], x['activos'][0][4]), reverse=True)[:10]
    top_10_riesgos_con_umbral = [(riesgo['riesgo'], riesgo['activos'][0][3]) for riesgo in top_10_riesgos]

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
                acciones.append(((actions,asociacion.usuario)))
    
    acciones_ordenadas = []
    acciones_finalizadas_canceladas = []
    otras_acciones = []


    for accion in acciones:
        if accion[0].estado in ['Finalizado', 'Cancelado']:
            acciones_finalizadas_canceladas.append(accion)
        else:
            otras_acciones.append(accion)
    acciones_ordenadas = sorted(otras_acciones, key=lambda x: abs((datetime.now() - datetime.combine(x[0].fechaFin, datetime.min.time())).total_seconds())) + acciones_finalizadas_canceladas
    return render_template('home/home.html', usuario=usuario, proyecto=proyecto, grafica=grafica, top10=top_10_riesgos_con_umbral, acciones=acciones_ordenadas[:10])

@home.route('/regresar-proyectos')
def regresarProyectos():
    session.pop('proyecto_id')
    return redirect(url_for('proyectos.vistaListaProyectos'))