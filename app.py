import streamlit as st
from PIL import Image as image2
import pandas as pd
import base64
import os
import logging
import time
import json

from Cafe_Color.read_features import Image
from Cafe_Color.preprocessing import Preprocess
from Cafe_Color.segmentation import ColorSegmentation
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io


# Configurar la página
st.set_page_config(layout="wide")

# Configurar el registro de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ruta para almacenar los usuarios registrados en un JSON 
USER_DATA_FILE = 'user_data.json'


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
                        "password": password
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
                    

# Credenciales de usuario (en un entorno real, utiliza un método seguro para almacenar y verificar credenciales)
USER_CREDENTIALS = {

                    "user": "1234",
                    "user2": "password2"
                   }

def exportar_a_pdf(dataframe):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Convertir el DataFrame a una lista de listas
    data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    elements = [table]
    pdf.build(elements)

    buffer.seek(0)
    return buffer.read()





def load_image(image_path):
    """Carga una imagen y la convierte a base64."""
    try:
        with open(image_path, "rb") as img_file:            
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error al cargar la imagen: {e}")
        logger.error(f"Error al cargar la imagen: {e}")
        return ""
    
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


# Controlar el flujo de la aplicación
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if not st.session_state['authenticated']:
    if st.session_state['show_register']:
        registro()  # Mostrar el registro si el usuario lo selecciona
    else:
        login()  # Mostrar la pantalla de inicio de sesión

else:

    st.success(f"Bienvenido {st.session_state['user_data']['nombre']}. Finca {st.session_state['user_data']['nombre_finca']}.")
    try:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio_actual, "logo2.png")
    except Exception as e:
        st.error(f"Error al obtener la ruta del directorio actual: {e}")
        logger.error(f"Error al obtener la ruta del directorio actual: {e}")

    image_base64 = load_image(ruta_logo) # Cargar y codificar la imagen del logo

    st.markdown( # CSS para la página
        """
        <style>
        .css-18e3th9 {
            padding-top: 0rem;
            padding-bottom: 10rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .css-1d391kg {
            padding-top: 3.5rem;
            padding-right: 1rem;
            padding-bottom: 3.5rem;
            padding-left: 1rem;
        }
        .title {
            text-align: center;
            font-size: 6vw; /* Ajusta el tamaño del título para dispositivos móviles */
            margin: 0; /* Reduce el espacio superior e inferior del título */
            padding-top: 0; /* Asegura que no haya espacio adicional en la parte superior */
        }
        .image-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0; /* Reduce el espacio entre la imagen y los radio buttons */
            padding: 0; /* Elimina el padding */
        }
        .image-container img {
            width: 60vw; /* Ajusta el tamaño de la imagen para dispositivos móviles */
            height: auto;
        }
        .radio-buttons-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0; /* Reduce el espacio entre los radio buttons y el siguiente contenido */
            padding: 0;
        }
        .radio-buttons-container label {
            margin: 0px; /* Reduce el margen entre los labels de los radio buttons */
            font-size: 5vw; /* Ajusta el tamaño de la fuente para los labels de los radio buttons */
        }
        .uploader-container {
            margin-top: 0; /* Reduce el espacio entre los radio buttons y el uploader */
            padding: 0; /* Elimina el padding */
        }
        .stRadio [role=radiogroup]{
            align-items: center;
            justify-content: center;
        }
        /* Estilo para las columnas de imágenes */
        .column-container {
            display: grid;
            grid-template-columns: 1fr 1fr; /* Dos columnas de igual tamaño */
            gap: 10px;
            justify-items: center;
            align-items: center;
        }
        .column-container img {
            width: 100%; /* Ajusta el tamaño de las imágenes al 100% del contenedor */
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # Mostrar el título y la imagen
    st.markdown(f'<h1 class="title">Clasificador de café cereza</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="image-container"><img src="data:image/png;base64,{image_base64}" alt="Logo"></div>', unsafe_allow_html=True)

    # Obtener la cantidad de lotes del usuario
    num_lotes = st.session_state['user_data']['lotes_finca']
    lotes = [f"Lote {i+1}" for i in range(num_lotes)]

    # Inicializar el estado de sesión si no está presente
    if 'selected_lote' not in st.session_state:
        st.session_state['selected_lote'] = lotes[0] if lotes else "Lote 1"
    if 'last_uploaded_file' not in st.session_state:
        st.session_state['last_uploaded_file'] = None


    # Inicializar el estado de sesión si no está presente
    if 'selected_option' not in st.session_state:
        st.session_state['selected_option'] = "Tomar foto"
    if 'last_uploaded_file' not in st.session_state:
        st.session_state['last_uploaded_file'] = None

    # Seleccionar el lote mediante un selectbox
    st.sidebar.header("Seleccionar Lote")
    selected_lote = st.sidebar.selectbox("", lotes)
    st.session_state['selected_lote'] = selected_lote

    # Crear una única columna para centrar el contenido
    col1 = st.columns([1])[0]

    # Colocar los radio buttons en la columna central
    with col1:
        st.markdown('<div class="radio-buttons-container">', unsafe_allow_html=True)
        method = st.radio(
            label="",
            options=["Tomar foto", "Cargar imagen"],
            index=["Tomar foto", "Cargar imagen"].index(st.session_state['selected_option']),
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Almacenar la selección en el estado de sesión
    st.session_state['selected_option'] = method
    show_image = False

    # Mostrar la interfaz según la selección
    st.markdown('<div class="uploader-container">', unsafe_allow_html=True)

    if method == "Cargar imagen":
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
        show_image = True

    else:
        uploaded_file = st.camera_input("")
        show_image = False

    # Mostrar la imagen seleccionada o tomada
    if uploaded_file is not None and show_image:
        image = image2.open(uploaded_file)
        st.image(image, use_column_width=True)


    if uploaded_file is not None and uploaded_file != st.session_state['last_uploaded_file']:
        st.session_state['last_uploaded_file'] = uploaded_file

        image = image2.open(uploaded_file) 
        path = "imagen_user.jpg"
        image.save(path)

        img = Image(path)
        img_normal = Preprocess(img)._normalize(_rembg_ = True, _white_reference_ = False)
        Color = ColorSegmentation(img_normal)
        results = Color.MaskLab_coffe(((22,99),(15,100)))

        # Utilizar la clase column-container para el contenedor de las imágenes
        st.markdown('<div class="column-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.image(results.good_sample, use_column_width=True) 

        #    #st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

        with col2:
            st.image(results.bad_sample, use_column_width=True)
            #st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café malo</p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


        # Crear el DataFrame para almacenar los resultados de las pruebas
        if 'results_list' not in st.session_state:
            st.session_state.results_list = []

        if uploaded_file is not None:
            num_prueba = len(st.session_state.results_list) + 1  # Obtener el número de prueba
            fecha_hora_actual = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtener la fecha y hora actual

            st.session_state.results_list.append({
                "#prueba": num_prueba,
                "Fecha y Hora": fecha_hora_actual,
                "Lote": selected_lote,
                "% cafe bueno": str(results.percent[0])[:6],
                "% cafe malo": str(results.percent[1])[:6]
            })

        # Mostrar la tabla de resultados
    if 'results_list' in st.session_state:
        st.markdown("<h2 style='text-align: center;'>Resultados de las pruebas</h2>", unsafe_allow_html=True)
        df_resultados = pd.DataFrame(st.session_state.results_list)
        st.table(df_resultados.style.set_properties(**{'text-align': 'center'}))

        # Agregar un botón para exportar y descargar la tabla como PDF
        pdf_content = exportar_a_pdf(df_resultados)  # Supón que esta función devuelve el contenido PDF en binario
        st.download_button(
            label="Descargar PDF",
            data=pdf_content,
            file_name='resultados_pruebas.pdf',
            mime='application/pdf'

        )

# Agregar un botón de cierre de sesión
    if st.session_state['authenticated']:
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.rerun() #