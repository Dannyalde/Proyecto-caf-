from mysql.connector import Error
from connection import conexion_DB



def insert_usuario_y_finca(cedula, nombre, contraseña, correo, celular, nombre_finca, direccion_finca, numero_lotes):
    try:
        # Conexión a la base de datos
        connection = conexion_DB()

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
            print(f"Usuario {nombre} registrado correctamente : {cursor.rowcount}")
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
        
        # Conexión a la base de datos
        connection = conexion_DB()

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
        connection = conexion_DB()

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

            query_ID_lote = """
            SELECT ID 
            FROM Lotes
            WHERE ID_usuario = %s AND N_lotes = %s  
            """

            cursor.execute(query_ID_lote, (ID_Usuario[0], lote))
            ID_lote = cursor.fetchone() 
            
            query_fotos = """
            INSERT INTO Fotos (ID_lote, porcentaje_bueno, porcentaje_malo, fecha, hora, nombre, ruta)
            VALUES (%s, %s, %s, %s, %s, %s ,%s)
            """

            cursor.execute(query_fotos, (ID_lote[0], porcentaje_bueno, porcentaje_malo, fecha, hora, nombre, ruta))

            connection.commit()
            print(f"Registro de foto insertado correctamente. ID_Usuario :  {ID_Usuario[0]},  ID_Lote : {ID_lote[0]}")
            cursor.close()


    except Error as e:
        if connection.is_connected():
            connection.rollback()  # Revertir cambios en caso de 
            print(f"Error insert fotos: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada")





