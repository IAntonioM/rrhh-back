
import os
import tempfile
from datetime import datetime
import jinja2
from weasyprint import HTML, CSS
from ..models.general.reporte import ReporteModel

class ReporteService:
    def __init__(self):
        # Rutas de directorios
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = os.path.join(self.base_dir, 'storage','templates')
        self.static_dir = os.path.join(self.base_dir, 'storage','templates','static')
        self.output_dir = os.path.join(self.base_dir, 'storage','temp_pdf')
        
        # Asegurarnos que los directorios existan
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configurar Jinja2
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
    
    def ejecutar_procedimiento(self, parametros, plantilla_nombre):
        """
        Ejecuta el procedimiento almacenado asociado a la plantilla
        """
        success, result = ReporteModel.ejecutar_procedimiento_reporte(parametros, plantilla_nombre)
        
        if not success:
            raise Exception(result)  # Propagar el error con el mensaje del SQL Server
                
        return result
    
    def verificar_plantilla(self, plantilla_nombre):
        """Verifica si la plantilla existe"""
        return os.path.exists(os.path.join(self.template_dir, plantilla_nombre))
    
    def generar_pdf(self, plantilla_nombre, parametros, datos,usuario_current):
        """
        Genera un PDF usando WeasyPrint basado en una plantilla HTML y datos
        """
        # Cargar la plantilla
        template = self.template_env.get_template(plantilla_nombre)
        
        # Renderizar la plantilla con los datos
        html_content = template.render(
            datos=datos,
            usuario_current=usuario_current,
            parametros=parametros,
            fecha_generacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Crear un archivo temporal para el HTML
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp.write(html_content.encode('utf-8'))
            html_path = tmp.name
        
        try:
            # Nombre del archivo de salida (usando timestamp para evitar colisiones)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            output_file = os.path.join(self.output_dir, f'reporte_{timestamp}.pdf')
            
            # Cargar CSS si existe
            css_files = []
            css_file = os.path.join(self.static_dir, 'styles.css')
            if os.path.exists(css_file):
                css_files.append(CSS(filename=css_file))
            
            # Generar el PDF con WeasyPrint
            HTML(filename=html_path).write_pdf(
                output_file, 
                stylesheets=css_files
            )
            
            return output_file, f'reporte_{timestamp}.pdf'
        
        finally:
            # Eliminar el archivo temporal HTML
            if os.path.exists(html_path):
                os.remove(html_path)
    
    def listar_plantillas(self):
        """Lista todas las plantillas disponibles"""
        return [f for f in os.listdir(self.template_dir) if f.endswith('.html')]