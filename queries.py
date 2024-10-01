
import mysql.connector
from mysql.connector import Error


def get_IDusuario_IDfinca_Nlotes(nombre_usuario):
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
            query_Usuarios = """
            SELECT ID, ID_finca
            FROM Usuarios
            WHERE nombre = %s 
            """
           
            cursor.execute(query_Usuarios, (nombre_usuario))
            result_Usuarios = cursor.fetchone()  # Devolverá None si no se encuentra un usuario

            query_fincas = """
            SELECT numero_lotes 
            FROM Fincas
            WHERE ID = %s 
            """

            if result_Usuarios:
                id_usuario, id_finca = result_Usuarios                
                cursor.execute(query_fincas, ([id_finca]))
                N_lotes = cursor.fetchone()
                print(f"Usuario autenticado correctamente. ID_usuario: {id_usuario}, ID_finca: {id_finca}, N_lotes: {N_lotes[0]}")
                return id_usuario, id_finca, N_lotes[0]
            else:
                print("Autenticación fallida. Cédula o contraseña incorrectos.")
                return None, None, None

    except Error as e:
        print(f"Error al autenticar usuario: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("Conexión cerrada")
            
            
