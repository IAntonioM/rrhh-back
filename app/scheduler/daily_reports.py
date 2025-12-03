from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar scheduler
scheduler = BackgroundScheduler()

def generar_reportes_diarios():
    """
    Job que se ejecuta diariamente a las 00:10
    """
    try:
        logger.info("🚀 Iniciando generación automática de reportes...")
        
        from models.reportes.PrediccionAusencias import PrediccionAusencias
        
        # Ejecutar pipeline
        result = PrediccionAusencias.ejecutar_pipeline_ml()
        
        if result['success']:
            logger.info(f"✅ Reportes generados exitosamente")
            logger.info(f"   - Timestamp: {result['timestamp']}")
            logger.info(f"   - Total registros: {result['total_registros']}")
        else:
            logger.error(f"❌ Error al generar reportes: {result['message']}")
            
    except Exception as e:
        logger.error(f"❌ Error crítico en job de reportes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def start_scheduler():
    """
    Inicia el scheduler con el job configurado
    """
    try:
        # Verificar si ya está corriendo
        if scheduler.running:
            logger.warning("⚠️  Scheduler ya está en ejecución")
            return
        
        # Configurar job para ejecutarse a las 00:10 todos los días
        scheduler.add_job(
            func=generar_reportes_diarios,
            trigger=CronTrigger(hour=0, minute=10),  # 00:10 AM
            id='generar_reportes_diarios',
            name='Generación diaria de reportes ML',
            replace_existing=True
        )
        
        # Iniciar scheduler
        scheduler.start()
        
        logger.info("✅ Scheduler iniciado correctamente")
        logger.info("   - Job: Generación de reportes ML")
        logger.info("   - Horario: Todos los días a las 00:10")
        
        # Mostrar próxima ejecución
        job = scheduler.get_job('generar_reportes_diarios')
        if job:
            next_run = job.next_run_time
            logger.info(f"   - Próxima ejecución: {next_run}")
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar scheduler: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def stop_scheduler():
    """
    Detiene el scheduler de forma segura
    """
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("✅ Scheduler detenido correctamente")
    except Exception as e:
        logger.error(f"❌ Error al detener scheduler: {str(e)}")


# Para testing: ejecutar job manualmente
def ejecutar_job_ahora():
    """
    Ejecuta el job de reportes inmediatamente (útil para testing)
    """
    logger.info("🧪 Ejecutando job manualmente...")
    generar_reportes_diarios()