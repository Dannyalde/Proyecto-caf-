import mysql.connector
from mysql.connector import Error




def insert_usuario(cedula, nombre, contraseña, correo, celular):
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',  # Cambia si es otro host
            database='dev_color_cafe',  # Nombre de tu base de datos
            user='root',  # Usuario de MySQL
            password='1009'  # Contraseña del usuario
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query de inserción
            query = """
            INSERT INTO Usuarios (cedula, nombre, contraseña, correo, celular)
            VALUES (%s, %s, %s, %s, %s)
            """
            # Valores a insertar
            valores = (cedula, nombre, contraseña, correo, celular)

            # Ejecutar el insert
            cursor.execute(query, valores)
            connection.commit()

            print(f"Registro insertado correctamente: {cursor.rowcount}")
            cursor.close()

    except Error as e:
        print(f"Error al insertar datos: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada")