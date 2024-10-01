
import mysql.connector

def conexion_DB():
    
    connection = mysql.connector.connect(
        host='localhost',
        database='dev_color_cafe',
        user='root',
        password='1009'
    )

    return connection
