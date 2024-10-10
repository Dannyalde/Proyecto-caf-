from Inserts import insert_usuario_y_finca, insert_lotes
from queries import get_IDusuario_IDfinca_Nlotes
from connection import conexion_DB

import streamlit as st
import bcrypt
import hashlib
import json
import time
import os


def verificar_usuario_existente(cedula, email):
    conexion = conexion_DB()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para verificar si el nombre de usuario o el correo ya existen
    query = "SELECT * FROM Usuarios WHERE cedula = %s OR correo = %s"
    cursor.execute(query, (cedula, email))
    usuario = cursor.fetchone()
    print(usuario)

    conexion.close()

    if usuario:
        return True  # El usuario o correo ya existen
    return False  # No existe el usuario ni el correo


# Función de registro
def registro():
    st.title("Registro de Nuevo Usuario")
    
    # Solicitar los datos del nuevo usuario
    nombre = st.text_input("Nombre completo")
    password = st.text_input("Contraseña", type="password")
    password_confirm = st.text_input("Confirmar contraseña", type="password")
    correo = st.text_input("Correo")
    celular = st.text_input("Celular")
    nombre_finca = st.text_input("Nombre de la finca")
    direccion_finca = st.text_input("Dirección de la finca")
    lotes_finca = st.number_input("Cantidad de lotes en la finca", min_value=1, step=1)
    cedula = st.text_input("Usuario (Cedula)")
    
    
    if st.button("Registrarse"):
        if not (nombre and correo and celular and nombre_finca and direccion_finca and cedula and password) and password_confirm:
            st.error("Por favor complete todos los campos")
        else: 

            if not nombre.replace(" ", "").isalpha():
                st.error("El nombre solo puede contener letras.") 
                    # Verificar que la cédula solo contenga números
            else: 
                if not cedula.isdigit():
                    st.error("La cédula solo puede contener números.")

                    # Verificar si las contraseñas coinciden
                else:            
                    if password != password_confirm:
                        st.error("Las contraseñas no coinciden.")
                    # Verificar si el usuario o correo ya están registrados
                    else: 
                        if verificar_usuario_existente(cedula, correo):
                            st.error("El nombre de usuario o correo ya están registrados. Intente con otros.")        

                        else:                            
                            insert_usuario_y_finca(cedula, nombre, password, correo, celular, nombre_finca, direccion_finca, lotes_finca)
                            id_usuario, id_finca, N_lotes = get_IDusuario_IDfinca_Nlotes([nombre])
                            insert_lotes(id_usuario, id_finca, N_lotes)       
                            st.success("¡Registro exitoso! Ya puede iniciar sesión.")
                            
                            st.session_state['show_register'] = False
                            st.session_state['just_registered'] = True
                            time.sleep(2)
                            st.rerun() # Volver al inicio de sesión
                            

def verificar_contraseña(password_ingresada, password_almacenada):
    # Almacena las contraseñas con un hash seguro
    return bcrypt.checkpw(password_ingresada.encode('utf-8'), password_almacenada.encode('utf-8'))

    
def autenticar_usuario(user_cc, password):
    conexion = conexion_DB()
    cursor = conexion.cursor(dictionary=True)

    # Consulta a la base de datos para obtener el usuario
    query_usuarios = "SELECT * FROM Usuarios WHERE cedula = %s"
    cursor.execute(query_usuarios, (user_cc,))
    data_usuario = cursor.fetchone()

    query_fincas = "SELECT * FROM Fincas WHERE ID = %s"
    cursor.execute(query_fincas, (data_usuario['ID_finca'],))
    data_finca = cursor.fetchone()

    conexion.close()

    if data_usuario:
        # Verifica la contraseña hasheada
        if verificar_contraseña(password, data_usuario['contraseña']):
            return data_usuario, data_finca  # Retorna los datos del usuario si la autenticación es correcta
    return None, None


def login():
    st.title("Inicio de Sesión")

    if 'just_registered' in st.session_state and st.session_state['just_registered']:
        st.success("¡Registro exitoso! Inicie sesión con sus credenciales.")
        st.session_state['just_registered'] = False  # Limpiar estado después de mostrar el mensaje

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    # Botón para registrarse
    if st.button("¿No tiene cuenta? Regístrese aquí"):
        st.session_state['show_register'] = True
        st.rerun()

    # Autenticar automáticamente cuando se ingresan las credenciales correctas
    if username and password:  # Solo verificar si ambos campos tienen algún valor
        print("Intentando autenticación...")
        data_usuario, data_finca = autenticar_usuario(username, password)

        if data_usuario:
            print("Usuario autenticado correctamente")
            st.session_state['authenticated'] = True
            st.session_state['user_data'] = data_usuario   # Guardar datos del usuario en sesión
            st.session_state['finca_data'] = data_finca 
            st.success(f"¡Inicio de sesión exitoso! Bienvenido {data_usuario['nombre']}")
            time.sleep(1)
            st.rerun()
            
        else:
            st.error("Usuario o contraseña incorrectos. Intente nuevamente.")

