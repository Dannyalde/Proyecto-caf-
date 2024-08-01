import streamlit as st
from PIL import Image
import pandas as pd
import source as sc
import cv2 as cv
import base64
import os

# Configurar la página
st.set_page_config(layout="wide")

# Obtener la ruta del directorio actual
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, "logo2.png")

def load_image(image_path):
    """Carga una imagen y la convierte a base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error al cargar la imagen: {e}")
        return ""

# Cargar y codificar la imagen del logo
image_base64 = load_image(ruta_logo)

# CSS para la página

st.markdown(
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

# Inicializar el estado de sesión si no está presente
if 'selected_option' not in st.session_state:
    st.session_state['selected_option'] = "Tomar foto"
if 'last_uploaded_file' not in st.session_state:
    st.session_state['last_uploaded_file'] = None

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
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)


if uploaded_file is not None and uploaded_file != st.session_state['last_uploaded_file']:
    st.session_state['last_uploaded_file'] = uploaded_file

    image = Image.open(uploaded_file) 
    path = "imagen_user.jpg"
    image.save(path)

    # Procesar la imagen
    img_03MP = cv.resize(cv.imread(path)[..., ::-1], (1536, 2048))
    img = img_03MP
    img_normal, ref_white, mean, sample = sc.Normal(img, white_limit=240)

    Lab = sc.RGB2Lab(img_normal)
    Malo, CafeMalo, Bueno, CafeBueno = sc.MaskLabV2(Lab, img_normal, sample, ((22, 99), (15, 100)))#

    # Utilizar la clase column-container para el contenedor de las imágenes
    st.markdown('<div class="column-container">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.image(Bueno.reshape(img_normal.shape), use_column_width=True)
    #    #st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

    with col2:
        st.image(Malo.reshape(img_normal.shape), use_column_width=True)
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
            "% cafe bueno": str(CafeBueno)[:6],
            "% cafe malo": str(CafeMalo)[:6]
        })

    # Mostrar la tabla de resultados
if 'results_list' in st.session_state:
    st.markdown("<h2 style='text-align: center;'>Resultados de las pruebas</h2>", unsafe_allow_html=True)
    df_resultados = pd.DataFrame(st.session_state.results_list)
    st.table(df_resultados.style.set_properties(**{'text-align': 'center'}))

    # Agregar un botón para exportar y descargar la tabla como PDF
    pdf_content = sc.exportar_a_pdf(df_resultados)  # Supón que esta función devuelve el contenido PDF en binario
    st.download_button(
        label="Descargar PDF",
        data=pdf_content,
        file_name='resultados_pruebas.pdf',
        mime='application/pdf'

    )