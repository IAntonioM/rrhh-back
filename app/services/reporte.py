
import os
import tempfile
from datetime import datetime
import jinja2
from weasyprint import HTML, CSS
import json
import tempfile
import pandas as pd
from ..models.general.reporte import ReporteModel

class ReporteService:
    def __init__(self):
        # Rutas de directorios
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = os.path.join(self.base_dir, 'storage','templates')
        self.static_dir = os.path.join(self.base_dir, 'storage','templates','static')
        self.output_dir = os.path.join(self.base_dir, 'storage','temp_pdf')
        #EXCEL
        self.excel_config_dir = os.path.join(self.base_dir, 'storage', 'excel_templates')
        self.excel_output_dir = os.path.join(self.base_dir, 'storage', 'temp_excel')
        
        # Asegurarnos que los directorios existan
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)     
        os.makedirs(self.excel_config_dir, exist_ok=True)
        os.makedirs(self.excel_output_dir, exist_ok=True)
        
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
    
    
    #EXCEL
    def verificar_plantilla_excel(self, plantilla_nombre):
        """Verifica si existe la plantilla de configuración de Excel"""
        return os.path.exists(os.path.join(self.excel_config_dir, plantilla_nombre))
    
    
    def generar_excel(self, plantilla_nombre, parametros, usuario_current, custom_title=None):
        # Cargar configuración de la plantilla
        with open(os.path.join(self.excel_config_dir, plantilla_nombre), 'r') as f:
            config = json.load(f)

        # Ejecutar procedimiento almacenado
        success, datos = ReporteModel.ejecutar_procedimiento_reporte_excel(
            parametros,
            config.get('procedure_name', 'sp_GenerarReporte')
        )

        if not success:
            raise Exception(f"Error en procedimiento: {datos}")

        # Convertir a DataFrame
        df = pd.DataFrame(datos)

        # Seleccionar solo las columnas definidas en la configuración
        column_mapping = config.get('columns', {})
        
        # Filtrar el DataFrame para incluir solo las columnas especificadas
        df = df[[col for col in column_mapping.keys()]]
        
        # Renombrar columnas según configuración
        df = df.rename(columns=column_mapping)

        # Formatear columnas
        column_formats = config.get('column_formats', {})
        for col, fmt in column_formats.items():
            display_col = column_mapping.get(col, col)
            if fmt == 'date':
                df[display_col] = pd.to_datetime(df[display_col]).dt.date
            elif fmt == 'currency':
                df[display_col] = df[display_col].apply(lambda x: f"${x:,.2f}")

        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = usuario_current[0]['username'] if usuario_current else 'usuario'
        filename_template = config.get('filename_template', 'Reporte_{fecha}_{usuario}.xlsx')
        filename = filename_template.format(fecha=timestamp, usuario=username)
        output_file = os.path.join(self.output_dir, filename)

        # Crear Excel con formato
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Configuraciones de estilo
            workbook = writer.book
            worksheet = writer.book.add_worksheet('Reporte')
            
            # Estilo para título principal
            titulo_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2ea2cc',
                'font_color': 'white'
            })
            
            # Estilo para subtítulo
            subtitulo_format = workbook.add_format({
                'italic': True,
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2ea2cc'
            })
            
            # Estilo para encabezados de columna
            header_style = config.get('styles', {}).get('header', {})
            header_format = workbook.add_format({
                'bold': header_style.get('bold', True),
                'bg_color': header_style.get('bg_color', '#2ea2cc'),
                'font_color': header_style.get('font_color', 'white'),
                'align': 'center',
                'valign': 'vcenter'
            })

            # Determinar título (personalizado o por defecto)
            titulo = custom_title or 'REPORTE _SIN TITULO CUSTOM'

            # Añadir título principal
            worksheet.merge_range('A1:F1', titulo, titulo_format)
            
            # Añadir subtítulo con fecha
            fecha_actual = datetime.now().strftime('%d de %B de %Y')
            worksheet.merge_range('A2:F2', f'Generado el {fecha_actual}', subtitulo_format)

            # Escribir encabezados de columna
            columnas = list(df.columns)
            for col_num, value in enumerate(columnas):
                worksheet.write(3, col_num, value, header_format)

            # Escribir datos
            for row_num, row_data in enumerate(df.values, start=4):
                for col_num, cell_value in enumerate(row_data):
                    worksheet.write(row_num, col_num, cell_value)

            # Ajustar ancho de columnas
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)

        return output_file, filename
 
    def listar_plantillas_excel(self):
        """Lista todas las plantillas de Excel disponibles"""
        return [f for f in os.listdir(self.excel_config_dir) if f.endswith('.json')]