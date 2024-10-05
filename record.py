from Inserts import insert_usuario_y_finca, insert_lotes
from queries import get_IDusuario_IDfinca_Nlotes

import streamlit as st
import json
import time
import os

# Ruta para almacenar los usuarios registrados en un JSON 
USER_DATA_FILE = 'user_data.json'

# Credenciales de usuario (en un entorno real, utiliza un método seguro para almacenar y verificar credenciales)
USER_CREDENTIALS = {
                    "user": "1234",
                    "user2": "password2"
                   }

# Función para cargar los usuarios desde el archivo JSON
def cargar_usuarios():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

# Función para guardar los usuarios en el archivo JSON
def guardar_usuarios(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

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
    username = st.text_input("Usuario (Cedula)")
    
    
    if st.button("Registrarse"):
        if not (nombre and correo and celular and nombre_finca and direccion_finca and username and password) and password_confirm:
            st.error("Por favor complete todos los campos")
        else:
            if password != password_confirm:
                st.error("Las contraseñas no coinciden.")
            else: 
                # Cargar usuarios existentes
                usuarios = cargar_usuarios()
                insert_usuario_y_finca(username, nombre, password, correo, celular, nombre_finca, direccion_finca, lotes_finca)
                id_usuario, id_finca, N_lotes = get_IDusuario_IDfinca_Nlotes([nombre])
                insert_lotes(id_usuario, id_finca, N_lotes)
                #path = os.path.join('Imagenes_usuarios', username)
                #if not os.path.exists(path):
                #    os.makedirs(path)

                # Verificar si el usuario ya existe
                if username in usuarios:
                    st.error("El nombre de usuario ya existe. Por favor elija otro.")
                else:
                    # Agregar nuevo usuario
                    usuarios[username] = {
                        "nombre": nombre,
                        "correo": correo,
                        "celular": celular,
                        "nombre_finca": nombre_finca,
                        "direccion_finca": direccion_finca,
                        "lotes_finca": lotes_finca,
                        "password": password, 
                        "cedula": username
                    }
                    
                    # Guardar los datos
                    guardar_usuarios(usuarios)
                    st.success("¡Registro exitoso! Ya puede iniciar sesión.")
                    
                   # Establecer una variable para volver al inicio de sesión
                    st.session_state['show_register'] = False
                    st.session_state['just_registered'] = True
                    time.sleep(2)
                    st.rerun()
 # Volver al inicio de sesión
                    
    
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
        usuarios = cargar_usuarios()
        if username in usuarios and usuarios[username]['password'] == password:
            st.session_state['authenticated'] = True
            st.session_state['user_data'] = usuarios[username]  # Guardar datos del usuario en sesión
            st.success("Inicio de sesión exitoso!")
            time.sleep(1)
            st.rerun()
            
        elif username in USER_CREDENTIALS or password:  # Si se ha intentado iniciar sesión
            st.error("Usuario o contraseña incorrectos")
