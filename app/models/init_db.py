from config import get_db_connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
     # Crear la tabla 'Usuarios'
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
        CREATE TABLE usuarios (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(50) UNIQUE NOT NULL,
            password NVARCHAR(255) NOT NULL,
            rol_id INT NOT NULL DEFAULT 1,
            estado INT NOT NULL DEFAULT 1,
            fecha_reg DATETIME  NOT NULL,
            operador_reg NVARCHAR(50)  NOT NULL,
            estacion_reg NVARCHAR(50)  NOT NULL,
            fecha_act DATETIME  NOT NULL,
            operador_act NVARCHAR(50)  NOT NULL,
            estacion_act NVARCHAR(50)  NOT NULL,
        )
    ''')

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Periodos' AND xtype='U')
        CREATE TABLE Periodos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            anio INT NOT NULL,
            mes INT NOT NULL,
            fecha_registro DATE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
