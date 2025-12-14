import os
import tempfile
from datetime import datetime
import jinja2
from weasyprint import HTML, CSS
import json
import tempfile
import pandas as pd
import importlib.util
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
        
        
        
        self.excel_config_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'excel_config')
        self.excel_plantillas_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'excel_plantillas')
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'reportes')
        
        # Crear directorios si no existen
        os.makedirs(self.excel_config_dir, exist_ok=True)
        os.makedirs(self.excel_plantillas_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
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
        Devuelve múltiples tablas
        """
        success, result = ReporteModel.ejecutar_procedimiento_reporte(parametros, plantilla_nombre)
        
        if not success:
            raise Exception(result)  # Propagar el error con el mensaje del SQL Server
                
        return result
    
    def ejecutar_procedimiento_legacy(self, parametros, plantilla_nombre):
        """
        Método legacy para compatibilidad con código existente
        Devuelve solo la primera tabla
        """
        success, result = ReporteModel.ejecutar_procedimiento_reporte_legacy(parametros, plantilla_nombre)
        
        if not success:
            raise Exception(result)
                
        return result
    
    def verificar_plantilla(self, plantilla_nombre):
        """Verifica si la plantilla existe"""
        return os.path.exists(os.path.join(self.template_dir, plantilla_nombre))
    
    def generar_pdf(self, plantilla_nombre, parametros, datos, usuario_current):
        """
        Genera un PDF usando WeasyPrint basado en una plantilla HTML y datos
        Maneja múltiples tablas de datos
        """
        # Cargar la plantilla
        template = self.template_env.get_template(plantilla_nombre)
        
        # Preparar datos para la plantilla
        # Si datos es una lista de tablas, usar la nueva estructura
        # Si datos es una lista simple, usar la estructura legacy
        template_data = {
            'datos': datos,
            'usuario_current': usuario_current,
            'parametros': parametros,
            'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Agregar acceso fácil a tablas individuales
        if isinstance(datos, list) and len(datos) > 0 and isinstance(datos[0], dict) and 'table_index' in datos[0]:
            # Nueva estructura con múltiples tablas
            template_data['tablas'] = datos
            template_data['tabla_principal'] = datos[0]['data'] if datos else []
            template_data['num_tablas'] = len(datos)
            
            # Crear acceso directo por índice
            for i, tabla in enumerate(datos):
                template_data[f'tabla_{i}'] = tabla['data']
                template_data[f'tabla_{i}_columnas'] = tabla['columns']
                template_data[f'tabla_{i}_filas'] = tabla['row_count']
        else:
            # Estructura legacy
            template_data['tabla_principal'] = datos
            template_data['num_tablas'] = 1
        
        # Renderizar la plantilla con los datos
        html_content = template.render(**template_data)
        
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
            
            print(f"DEBUG - PDF escrito en: {output_file}")  # AGREGAR ESTE LOG
            print(f"DEBUG - Tamaño del archivo: {os.path.getsize(output_file)} bytes")  # AGREGAR ESTE LOG

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
        """
        Genera Excel con soporte para múltiples tablas
        """
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

        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = usuario_current[0]['username'] if usuario_current else 'usuario'
        filename_template = config.get('filename_template', 'Reporte_{fecha}_{usuario}.xlsx')
        filename = filename_template.format(fecha=timestamp, usuario=username)
        output_file = os.path.join(self.output_dir, filename)

        # Crear Excel con formato
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Determinar si usar múltiples tablas o una sola
            usar_multiples_tablas = config.get('multiple_tables', False)
            tabla_especifica = config.get('table_index', 0)  # Tabla específica a usar si no es múltiple
            
            if usar_multiples_tablas and len(datos) > 1:
                # Crear múltiples hojas para cada tabla
                for i, tabla_data in enumerate(datos):
                    sheet_name = config.get('sheet_names', {}).get(str(i), f'Tabla_{i}')
                    self._crear_hoja_excel(
                        writer, workbook, tabla_data, config, 
                        sheet_name, custom_title, i
                    )
            else:
                # Usar solo una tabla específica
                tabla_data = datos[tabla_especifica] if tabla_especifica < len(datos) else datos[0]
                self._crear_hoja_excel(
                    writer, workbook, tabla_data, config, 
                    'Reporte', custom_title, tabla_especifica
                )

        return output_file, filename
    
    def _crear_hoja_excel(self, writer, workbook, tabla_data, config, sheet_name, custom_title, table_index):
        """
        Crea una hoja individual de Excel con los datos de una tabla
        """
        # Convertir datos a DataFrame
        df = pd.DataFrame(tabla_data['data'])
        
        if df.empty:
            # Crear hoja vacía si no hay datos
            worksheet = workbook.add_worksheet(sheet_name)
            worksheet.write(0, 0, f"No hay datos para {sheet_name}")
            return

        # Configuración de columnas específica por tabla
        table_config = config.get('tables', {}).get(str(table_index), config)
        column_mapping = table_config.get('columns', {})
        
        # Filtrar y renombrar columnas si se especifica mapeo
        if column_mapping:
            # Filtrar el DataFrame para incluir solo las columnas especificadas
            available_cols = [col for col in column_mapping.keys() if col in df.columns]
            df = df[available_cols]
            # Renombrar columnas según configuración
            df = df.rename(columns=column_mapping)

        # Formatear columnas
        column_formats = table_config.get('column_formats', {})
        for col, fmt in column_formats.items():
            display_col = column_mapping.get(col, col)
            if display_col in df.columns:
                if fmt == 'date':
                    df[display_col] = pd.to_datetime(df[display_col], errors='coerce').dt.date
                elif fmt == 'currency':
                    df[display_col] = df[display_col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")

        # Crear hoja de trabajo
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Configuraciones de estilo
        titulo_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2ea2cc',
            'font_color': 'white'
        })
        
        subtitulo_format = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2ea2cc'
        })
        
        header_style = table_config.get('styles', {}).get('header', {})
        header_format = workbook.add_format({
            'bold': header_style.get('bold', True),
            'bg_color': header_style.get('bg_color', '#2ea2cc'),
            'font_color': header_style.get('font_color', 'white'),
            'align': 'center',
            'valign': 'vcenter'
        })

        # Determinar título
        titulo = custom_title or table_config.get('title', f'REPORTE - {sheet_name}')
        col_span = max(len(df.columns), 1)

        # Añadir título principal
        worksheet.merge_range(0, 0, 0, col_span - 1, titulo, titulo_format)
        
        # Añadir subtítulo con fecha
        fecha_actual = datetime.now().strftime('%d de %B de %Y')
        worksheet.merge_range(1, 0, 1, col_span - 1, f'Generado el {fecha_actual}', subtitulo_format)

        # Escribir encabezados de columna
        for col_num, value in enumerate(df.columns):
            worksheet.write(3, col_num, value, header_format)

        # Escribir datos
        for row_num, row_data in enumerate(df.values, start=4):
            for col_num, cell_value in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_value)

        # Ajustar ancho de columnas
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(max_len, 50))  # Limitar ancho máximo
 
    def listar_plantillas_excel(self):
        """Lista todas las plantillas de Excel disponibles"""
        return [f for f in os.listdir(self.excel_config_dir) if f.endswith('.json')]
    
    
    # NBUEVO
    
    def verificar_plantilla_python(self, plantilla_nombre):
        """Verifica si existe la plantilla Python"""
        plantilla_path = os.path.join(self.excel_plantillas_dir, plantilla_nombre)
        return os.path.exists(plantilla_path)

    def generar_excel_python(self, plantilla_nombre, parametros, usuario_current, custom_title=None):
        """
        Genera Excel usando plantilla Python para máxima flexibilidad
        """
        # Cargar y ejecutar la plantilla Python
        plantilla_path = os.path.join(self.excel_plantillas_dir, plantilla_nombre)
        
        # Importar dinámicamente la plantilla
        spec = importlib.util.spec_from_file_location("plantilla_reporte", plantilla_path)
        plantilla_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plantilla_module)
        
        # Crear instancia de la plantilla
        plantilla_instance = plantilla_module.PlantillaReporte()
        
        # Obtener configuración de la plantilla
        config = plantilla_instance.get_config()
        
        # Obtener datos usando el método de la plantilla
        datos = plantilla_instance.obtener_datos(parametros)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = usuario_current[0]['username'] if usuario_current else 'usuario'
        filename_template = config.get('filename_template', 'Reporte_{fecha}_{usuario}.xlsx')
        filename = filename_template.format(fecha=timestamp, usuario=username)
        output_file = os.path.join(self.output_dir, filename)

        # Crear Excel con formato
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Procesar cada tabla según la configuración
            for tabla_config in config.get('tablas', []):
                tabla_index = tabla_config.get('tabla_index', 0)
                
                # Verificar si existe la tabla
                if tabla_index >= len(datos):
                    continue
                    
                tabla_data = datos[tabla_index]
                
                # Procesar datos usando el método de la plantilla
                df_procesado = plantilla_instance.procesar_tabla(tabla_data, tabla_config)
                
                # Crear hoja
                sheet_name = tabla_config.get('sheet_name', f'Tabla_{tabla_index}')
                self._crear_hoja_excel_python(
                    writer, workbook, df_procesado, tabla_config, 
                    sheet_name, custom_title, plantilla_instance
                )

        return output_file, filename
    
    def _crear_hoja_excel_python(self, writer, workbook, df, tabla_config, sheet_name, custom_title, plantilla_instance):
        """
        Crea una hoja individual de Excel usando la configuración de la plantilla Python
        """
        if df.empty:
            # Crear hoja vacía si no hay datos
            worksheet = workbook.add_worksheet(sheet_name)
            worksheet.write(0, 0, f"No hay datos para {sheet_name}")
            return

        # Crear hoja de trabajo
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Obtener estilos de la plantilla
        estilos = plantilla_instance.get_estilos(workbook)
        
        # Determinar título
        titulo = custom_title or tabla_config.get('titulo', f'REPORTE - {sheet_name}')
        col_span = max(len(df.columns), 1)

        # Añadir título principal
        worksheet.merge_range(0, 0, 0, col_span - 1, titulo, estilos['titulo'])
        
        # Añadir subtítulo con fecha
        fecha_actual = datetime.now().strftime('%d de %B de %Y')
        worksheet.merge_range(1, 0, 1, col_span - 1, f'Generado el {fecha_actual}', estilos['subtitulo'])

        # Escribir encabezados de columna
        for col_num, value in enumerate(df.columns):
            worksheet.write(3, col_num, value, estilos['header'])

        # Escribir datos
        for row_num, row_data in enumerate(df.values, start=4):
            for col_num, cell_value in enumerate(row_data):
                # Aplicar formato específico si está definido
                formato = estilos.get('datos', None)
                worksheet.write(row_num, col_num, cell_value, formato)

        # Aplicar configuraciones específicas de la plantilla
        plantilla_instance.aplicar_configuraciones_hoja(worksheet, df, tabla_config)

    def listar_plantillas_python(self):
        """Lista todas las plantillas Python disponibles"""
        return [f for f in os.listdir(self.excel_plantillas_dir) if f.endswith('.py')]