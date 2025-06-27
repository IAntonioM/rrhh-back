# Test simple para diagnosticar el problema
import pyodbc
from config import get_db_connection

def test_marcacion_simple():
    """
    Test simple para diagnosticar el problema de marcaciones
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Test 1: Ejecutar SP directamente sin fetchone
        print("=== TEST 1: SP sin fetchone ===")
        try:
            cursor.execute("""
                EXEC [dbo].[SP_MARCACIONES]
                    @mquery = 1,
                    @fechaMarcacion = '2025-06-26',
                    @horaMarcacion = '08:20',
                    @idEmpleado = 2117,
                    @observacion = 'Test desde Python',
                    @estacion = 'TEST-PC',
                    @operador = 'test_user'
            """)
            conn.commit()
            print("✓ SP ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 2: Verificar si se insertó el registro
        print("\n=== TEST 2: Verificar inserción ===")
        try:
            cursor.execute("""
                SELECT TOP 1 * FROM marcacion 
                WHERE idEmpleado = 2117 
                AND observacion = 'Test desde Python'
                ORDER BY fecha_registro DESC
            """)
            result = cursor.fetchone()
            if result:
                print("✓ Registro encontrado en la tabla")
                print(f"ID Marcación: {result[0] if len(result) > 0 else 'N/A'}")
            else:
                print("✗ No se encontró el registro")
        except Exception as e:
            print(f"✗ Error al verificar: {e}")
        
        # Test 3: Probar con SELECT explícito
        print("\n=== TEST 3: SP con SELECT explícito ===")
        try:
            cursor.execute("""
                DECLARE @result VARCHAR(100)
                
                EXEC [dbo].[SP_MARCACIONES]
                    @mquery = 1,
                    @fechaMarcacion = '2025-06-26',
                    @horaMarcacion = '08:25',
                    @idEmpleado = 2117,
                    @observacion = 'Test con SELECT',
                    @estacion = 'TEST-PC',
                    @operador = 'test_user'
                
                SELECT 'SUCCESS' as status, 'Marcación registrada' as message
            """)
            
            result = cursor.fetchone()
            conn.commit()
            print(f"✓ Resultado: {result}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test 4: Verificar estructura del SP
        print("\n=== TEST 4: Verificar SP existe ===")
        try:
            cursor.execute("""
                SELECT name FROM sys.procedures 
                WHERE name = 'SP_MARCACIONES'
            """)
            result = cursor.fetchone()
            if result:
                print("✓ SP_MARCACIONES existe")
            else:
                print("✗ SP_MARCACIONES no encontrado")
        except Exception as e:
            print(f"✗ Error: {e}")
            
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        if conn:
            conn.close()

# Ejecutar el test
if __name__ == "__main__":
    test_marcacion_simple()