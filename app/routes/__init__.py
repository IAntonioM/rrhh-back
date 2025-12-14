from flask import Blueprint

from app.routes.planilla.periodos import periodos_bp
from app.routes.seguridad.auth import auth_bp
from app.routes.planilla.empleado import empleado_bp
from app.routes.planilla.condicion_laboral import condicion_laboral_bp
from app.routes.general.centro_costo import centro_costo_bp
from app.routes.general.cargo import cargo_bp
from app.routes.general.ubicacion import ubicacion_bp
from app.routes.seguridad.menu import menu_bp
from app.routes.general.conceptosMuni import conceptos_muni_bp
from app.routes.planilla.emp_concepto import emp_concepto_bp
from app.routes.general.banco import banco_bp
from app.routes.general.sede import sede_bp
from app.routes.planilla.regimenPensionarioSUNAT import regimen_pensionario_bp
from app.routes.planilla.Egresos import egresos_bp
from app.routes.planilla.Ingresos import ingresos_bp
from app.routes.planilla.Aportaciones import aportaciones_bp
from app.routes.general.conceptoPDT import conceptos_bp
from app.routes.tipoMonto import tipoMonto_bp
from app.routes.seguridad.acceso import acceso_bp
from app.routes.seguridad.rol import rol_bp
from app.routes.seguridad.usuario import usuario_bp
from app.routes.seguridad.rolmenu import rol_menu_bp
from app.routes.seguridad.rolmenuacceso import rol_menu_acceso_bp
from app.routes.planilla.trayectoria_laboral import trayectoria_laboral_bp
from app.routes.planilla.composicion_familiar import composicion_familiar_bp
from app.routes.planilla.vinculo_familiar import vinculo_familiar_bp
from app.routes.planilla.estado_civil import estado_civil_bp
from app.routes.terceros.terceros import terceros_bp
from app.routes.general.configuracion import configuraciones_bp
from app.routes.general.configuracionv2 import configuracionesv2_bp
from app.routes.terceros.ordenServicio import orden_servicio_bpv2
from app.routes.general.reporte import reporte_blueprint
from app.routes.tercerosv2.registro_locador import locador_contrato_bp
from app.routes.general.file import file_bp
from app.routes.general.datosPersonales import datos_personales_bp
from app.routes.terceros.control_contrato import control_contrato_bp
from app.routes.controlAsistencias.horarioRoute import horario_bp
from app.routes.controlAsistencias.marcacionRoute import marcaciones_bp
from app.routes.controlAsistencias.papeletasRoute import papeletas_bp
from app.routes.controlAsistencias.papeletasRRHHRoute import papeletas_rrhh_bp
from app.routes.controlAsistencias.papeletasSegRoute import papeletas_seg_bp
from app.routes.controlAsistencias.papeletasJefeRoute import papeletas_jefe_bp
from app.routes.controlAsistencias.asistenciasRoute import asistencias_bp
from app.routes.general.registro_tiempo import tiempo_procesamiento_bp
from app.routes.planilla.periodoRoute import periodo_bp
from app.routes.planilla.subsidiosRoute import subsidio_bp
from app.routes.planilla.grupo import grupo_bp
from app.routes.tercerosv2.emp_horario import emp_horario_bp
from app.routes.reportes.prediccion_ausencias_bp import prediccion_ausencias_bp
from app.routes.controlAsistencias.reportesAsistenciaRoute import reportes_asistencia_bp


# Función para registrar todas las rutas
def register_blueprints(app):
    app.register_blueprint(periodos_bp, url_prefix='/api/periodos')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(empleado_bp, url_prefix='/api/empleado')
    app.register_blueprint(condicion_laboral_bp, url_prefix='/api/condicion_laboral')
    app.register_blueprint(centro_costo_bp, url_prefix='/api/centro_costo')
    app.register_blueprint(cargo_bp, url_prefix='/api/cargo')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(ubicacion_bp, url_prefix='/api/ubicacion')
    app.register_blueprint(conceptos_muni_bp, url_prefix='/api/conceptosMuni')
    app.register_blueprint(emp_concepto_bp, url_prefix='/api/emp_concepto')
    app.register_blueprint(banco_bp, url_prefix='/api/banco')
    app.register_blueprint(sede_bp, url_prefix='/api/sede')
    app.register_blueprint(regimen_pensionario_bp, url_prefix='/api/regimen_pensionario_sunat')
    app.register_blueprint(egresos_bp, url_prefix='/api/egresos')
    app.register_blueprint(ingresos_bp, url_prefix='/api/ingresos')
    app.register_blueprint(aportaciones_bp, url_prefix='/api/aportaciones')
    app.register_blueprint(conceptos_bp, url_prefix='/api/conceptosPDT')
    app.register_blueprint(tipoMonto_bp, url_prefix='/api/tipoMonto')
    app.register_blueprint(acceso_bp, url_prefix='/api/acceso')
    app.register_blueprint(rol_bp, url_prefix='/api/rol')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuario')
    app.register_blueprint(rol_menu_bp, url_prefix='/api/rol_menu')
    app.register_blueprint(rol_menu_acceso_bp, url_prefix='/api/rol_menu_acceso')
    app.register_blueprint(trayectoria_laboral_bp, url_prefix='/api/trayectoria_laboral')
    app.register_blueprint(composicion_familiar_bp, url_prefix='/api/composicion_familiar')
    app.register_blueprint(vinculo_familiar_bp, url_prefix='/api/vinculo_familiar')
    app.register_blueprint(estado_civil_bp, url_prefix='/api/estado_civil')
    app.register_blueprint(terceros_bp, url_prefix='/api/terceros')    
    app.register_blueprint(configuraciones_bp, url_prefix='/api/configuracion')
    app.register_blueprint(configuracionesv2_bp, url_prefix='/api/configuracionv2')
    app.register_blueprint(orden_servicio_bpv2, url_prefix='/apiv2/orden-servicio')
    app.register_blueprint(reporte_blueprint, url_prefix='/api/reporte')
    app.register_blueprint(locador_contrato_bp, url_prefix='/api/locador_contrato')
    app.register_blueprint(file_bp, url_prefix='/api/file')
    app.register_blueprint(datos_personales_bp, url_prefix='/api/datos-personales')
    app.register_blueprint(control_contrato_bp, url_prefix='/api/control_contrato')
    app.register_blueprint(horario_bp, url_prefix='/api/horario')
    app.register_blueprint(marcaciones_bp, url_prefix='/api/marcaciones')
    app.register_blueprint(papeletas_bp, url_prefix='/api/papeletas')
    app.register_blueprint(papeletas_rrhh_bp, url_prefix='/api/papeletas_rrhh')
    app.register_blueprint(papeletas_seg_bp, url_prefix='/api/papeletas_seg')
    app.register_blueprint(papeletas_jefe_bp, url_prefix='/api/papeletas_jefe')
    app.register_blueprint(asistencias_bp, url_prefix='/api/asistencias')
    app.register_blueprint(tiempo_procesamiento_bp, url_prefix='/api/tiempo-procesamiento')
    app.register_blueprint(periodo_bp, url_prefix='/api/periodo')
    app.register_blueprint(subsidio_bp, url_prefix='/api/subsidio')
    app.register_blueprint(grupo_bp, url_prefix='/api/grupo')
    app.register_blueprint(emp_horario_bp, url_prefix='/api/emp_horario')    
    app.register_blueprint(prediccion_ausencias_bp, url_prefix='/api/reportes/prediccion')    
    app.register_blueprint(reportes_asistencia_bp, url_prefix='/api/reportes-asistencia')
    
    
    #     app.register_blueprint(periodo_bp, url_prefix='/api/periodo')
    # app.register_blueprint(subsidio_bp, url_prefix='/api/subsidio')
    # app.register_blueprint(grupo_bp, url_prefix='/api/grupo')
    # app.register_blueprint(reporte_ia_bp, url_prefix='/api/reporte-ia')



