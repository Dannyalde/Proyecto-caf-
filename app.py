from PIL import Image as image2
from datetime import datetime
import streamlit as st
import pandas as pd
import os
import logging
from io import BytesIO
from PIL import Image as ImagePIL


from record import registro, login
from data import load_image, exportar_a_pdf
from Inserts import inserts_fotos
from connection import conexion_cloudinary

from Cafe_Color.read_features import Image
from Cafe_Color.preprocessing import Preprocess
from Cafe_Color.segmentation import ColorSegmentation

import cloudinary
import cloudinary.uploader
import cloudinary.api



conexion_cloudinary()

# Configurar la página
st.set_page_config(layout="wide")

# Configurar el registro de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    lote_user = selected_lote[-1]
    print(f"EL usuario con la cedula {st.session_state['user_data']['cedula']} ha seleccionado el lote numero {lote_user}")

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
        carpeta_destino = st.session_state['user_data']['cedula'] 
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f'lote_{lote_user}_{fecha_hora}.png'
        folder_name = f"{carpeta_destino}"
        public_id = f"{nombre_archivo.split('.')[0]}"
        #ruta_imagen = os.path.join('Imagenes_usuarios', carpeta_destino, nombre_archivo)
        image.save(nombre_archivo)
        

        try:
            upload_result = cloudinary.uploader.upload(
                nombre_archivo, 
                folder = carpeta_destino + "_" + "lote" + "_" + lote_user,
                public_id = public_id )
            print("Imagen cargada correctamente a coludinary :", upload_result["secure_url"])
            
        except Exception as e:
            st.error(f"Error al subir la imagen a Cloudinary: {e}")

        img = Image(nombre_archivo)
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
            Now = pd.Timestamp.now()

            st.session_state.results_list.append({
                "#prueba": num_prueba,
                "Fecha y Hora": fecha_hora_actual,
                "Lote": selected_lote,
                "% cafe bueno": str(results.percent[0])[:6],
                "% cafe malo": str(results.percent[1])[:6]
            })
            inserts_fotos([st.session_state['user_data']['cedula']], lote_user, str(results.percent[0])[:6], str(results.percent[1])[:6], Now.date(), Now.time(), nombre_archivo,  upload_result["secure_url"])

            if os.path.exists(nombre_archivo):
                os.remove(nombre_archivo)
                print(f"se elimino la imagen {nombre_archivo}")


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