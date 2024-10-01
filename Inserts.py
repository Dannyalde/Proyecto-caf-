import mysql.connector
from mysql.connector import Error




def insert_usuario_y_finca(cedula, nombre, contraseña, correo, celular, nombre_finca, direccion_finca, numero_lotes):
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
            connection.start_transaction()

            query_finca = """
            INSERT INTO Fincas (nombre, direccion, numero_lotes)
            VALUES (%s, %s, %s )
            """

            cursor.execute(query_finca, (nombre_finca, direccion_finca, numero_lotes))
            finca_id = cursor.lastrowid  # Recupera el ID autogenerado de la finca

            query_usuario = """
            INSERT INTO Usuarios (cedula, nombre, contraseña, correo, celular, ID_finca)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Ejecutar el insert usuarios 
            cursor.execute(query_usuario, (cedula, nombre, contraseña, correo, celular, finca_id))
           
            connection.commit()
            print(f"Registro insertado correctamente: {cursor.rowcount}")
            cursor.close()

    except Error as e:
        if connection.is_connected():
            connection.rollback()  # Revertir cambios en caso de error
            
    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada")
            


def insert_lotes(id_usuario, id_finca, N_lotes):

    try: 
        
        print("Inicia insert lotes")
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',  # Cambia si es otro host
            database='dev_color_cafe',  # Nombre de tu base de datos
            user='root',  # Usuario de MySQL
            password='1009'  # Contraseña del usuario
        )

        if connection.is_connected():
            cursor = connection.cursor()
            connection.start_transaction()

            query_lotes = """
            INSERT INTO Lotes (ID_usuario, ID_finca, N_lotes)
            VALUES (%s, %s, %s )
            """

            for i in range(1, N_lotes+1,1): 

                cursor.execute(query_lotes, (id_usuario, id_finca, i))                
                print(f"Registro insertado correctamente: Lote # {i}")
            connection.commit()
            


    except Error as e:
        print("No se realizaron inserts lotes")
        if connection.is_connected():
            connection.rollback()  # Revertir cambios en caso de error
            
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

           

def inserts_fotos(cedula, lote, porcentaje_bueno,  porcentaje_malo, fecha, hora, nombre, ruta ):

    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='dev_color_cafe',
            user='root',
            password='1009'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Consulta para verificar las credenciales del usuario
            query_ID_usuario = """
            SELECT ID 
            FROM Usuarios
            WHERE cedula = %s 
            """
           
            cursor.execute(query_ID_usuario, (cedula))
            ID_Usuario = cursor.fetchone() 
            print("Este es el id del usuario :" , ID_Usuario[0], type(ID_Usuario[0]))


            query_ID_lote = """
            SELECT ID 
            FROM Lotes
            WHERE ID_usuario = %s AND N_lotes = %s  
            """

            cursor.execute(query_ID_lote, (ID_Usuario[0], lote))
            ID_lote = cursor.fetchone() 
            print("Este es el id del lote :" , ID_lote[0], type(ID_lote[0]))

            
            query_fotos = """
            INSERT INTO Fotos (ID_lote, porcentaje_bueno, porcentaje_malo, fecha, hora, nombre, ruta)
            VALUES (%s, %s, %s, %s, %s, %s ,%s)
            """

            cursor.execute(query_fotos, (ID_lote[0], porcentaje_bueno, porcentaje_malo, fecha, hora, nombre, ruta))

            connection.commit()
            print(f"Registro insertado correctamente: {cursor.rowcount}")
            cursor.close()


    except Error as e:
        if connection.is_connected():
            connection.rollback()  # Revertir cambios en caso de 
            print(f"Error insert fotos: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada")





