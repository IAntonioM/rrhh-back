import pandas as pd
import os
from datetime import datetime
import xlsxwriter

class OrdenServicioReporteExcel:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generar_excel(self, parametros, usuario_current, custom_title=None):
        # Ejecutar procedimiento almacenado (simulated here)
        success, datos = self._ejecutar_procedimiento_reporte(parametros)

        if not success:
            raise Exception(f"Error en procedimiento: {datos}")

        # Convertir a DataFrame
        df = pd.DataFrame(datos)

        # Definir mapeo de columnas
        column_mapping = {
            'num_servicio': 'Nro O/S',
            'DNI': 'DNI',
            'proveedor_nombres': 'Proveedor',
            'concepto_servicio': 'Concepto',
            'centroCosto_nombre': 'Area',
            'estado_os': 'Estado O/S',
            'fecha_orden': 'Fecha O/S'
        }

        # Renombrar columnas
        df = df.rename(columns=column_mapping)

        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = usuario_current[0]['username'] if usuario_current else 'usuario'
        filename = f"Reporte_Orden_Servicio_{timestamp}.xlsx"
        output_file = os.path.join(self.output_dir, filename)

        # Crear Excel con formato
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = writer.book.add_worksheet('Reporte Ordenes de Servicio')

            # Definir estilos
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
                'bg_color': '#2ea2cc',
                'font_color': 'white'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2ea2cc',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter'
            })

            subtotal_format = workbook.add_format({
                'bold': True,
                'bg_color': '#E6E6E6',
                'align': 'right'
            })

            total_format = workbook.add_format({
                'bold': True,
                'bg_color': '#B8CCE4',
                'align': 'right'
            })

            # Título principal
            titulo = custom_title or 'REPORTE DE ÓRDENES DE SERVICIO'
            worksheet.merge_range('A1:G1', titulo, titulo_format)
            
            # Subtítulo con fecha
            fecha_actual = datetime.now().strftime('%d de %B de %Y')
            worksheet.merge_range('A2:G2', f'Generado el {fecha_actual}', subtitulo_format)

            # Agrupar por área
            df_grouped = df.groupby('Area')

            # Variable para trackear la fila actual
            current_row = 2

            # Contador para total general
            total_ordenes = 0
            total_general_areas = {}

            # Iterar sobre cada área
            for area, group in df_grouped:
                # Encabezado de área
                current_row += 1
                worksheet.merge_range(f'A{current_row+1}:G{current_row+1}', f'ÁREA: {area}', header_format)
                current_row += 1

                # Escribir encabezados de columna
                columnas = list(group.columns)
                for col_num, value in enumerate(columnas):
                    worksheet.write(current_row, col_num, value, header_format)
                current_row += 1

                # Escribir datos del grupo
                for row_data in group.values:
                    for col_num, cell_value in enumerate(row_data):
                        worksheet.write(current_row, col_num, cell_value)
                    current_row += 1

                # Calcular subtotal de órdenes por área
                subtotal_ordenes = len(group)
                total_ordenes += subtotal_ordenes

                # Escribir subtotal de órdenes por área
                worksheet.write(current_row, 0, 'Subtotal Órdenes', subtotal_format)
                worksheet.write(current_row, 1, subtotal_ordenes, subtotal_format)
                current_row += 1

                # Guardar subtotal por área para total general
                total_general_areas[area] = subtotal_ordenes

                # Espacio entre áreas
                current_row += 1

            # Escribir total general
            worksheet.write(current_row, 0, 'TOTAL GENERAL DE ÓRDENES', total_format)
            worksheet.write(current_row, 1, total_ordenes, total_format)

            # Ajustar ancho de columnas
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)

        return output_file, filename

    def _ejecutar_procedimiento_reporte(self, parametros):
        # Simulated method to fetch data
        # In real implementation, this would call your database procedure
        try:
            # Ejemplo de datos simulados
            datos = [
                {
                    'num_servicio': f'OS-{i}',
                    'DNI': f'DNI-{1000+i}',
                    'proveedor_nombres': f'Proveedor {i}',
                    'concepto_servicio': f'Servicio {i}',
                    'centroCosto_nombre': 'Recursos Humanos' if i % 3 == 0 else 'Tecnología',
                    'estado_os': 'Activo' if i % 2 == 0 else 'Pendiente',
                    'fecha_orden': f'2024-01-{i+1:02d}'
                } for i in range(20)
            ]
            return True, datos
        except Exception as e:
            return False, str(e)