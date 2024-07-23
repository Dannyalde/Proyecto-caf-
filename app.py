import streamlit as st
import pandas as pd
from PIL import Image
import source as sc
import numpy as np
import cv2 as cv
import os

st.set_page_config(layout="wide")  # Configurar el ancho de la página
directorio_actual = os.path.dirname(os.path.abspath(__file__))  # Obtener la ruta del directorio actual (donde se encuentra el archivo principal)
ruta_logo_izquierdo = os.path.join(directorio_actual, r"logo_cafe.png")  # rutas de los logos
ruta_logo_derecho = os.path.join(directorio_actual, r"logoUA.png")

logo_izquierdo = Image.open(ruta_logo_izquierdo)  # Cargar las imágenes
logo_derecho = Image.open(ruta_logo_derecho)

# CSS para alinear columnas y hacerlas responsivas
st.markdown(
    """
    <style>
    @media (max-width: 600px) {
        .column-container {
            flex-direction: column;
        }
        .column {
            width: 100% !important;
        }
        .image-container {
            justify-content: center !important;
        }
        .centered-text {
            text-align: center !important;
        }
    }
    .column-container {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .column {
        flex: 1;
        padding: 10px;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        flex-direction: column;
        height: 100%;
    }
    .image-container img {
        max-width: 100%;
        height: auto;
    }
    .centered-text {
        text-align: center;
        font-size: 18px;
        color: black;
        font-weight: bold;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Crear las columnas
col1, col2, col3 = st.columns([0.35, 0.35, 0.5])

# Insertar las imágenes dentro de contenedores para forzar alineación
with col1:
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(logo_izquierdo, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(logo_derecho, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Título centrado en la página
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 30px;'>Bienvenidos a la aplicación para clasificar café</h1>", unsafe_allow_html=True)

if 'results_list' not in st.session_state:  # Crear el DataFrame para almacenar los resultados de las pruebas
    st.session_state.results_list = []

# Seleccionar método de carga de imagen
method = col2.radio(" ", ["Tomar una foto con la cámara", "Cargar imagen desde el computador",])

uploaded_file = None
if method == "Cargar imagen desde el computador":
    uploaded_file = col2.file_uploader("Cargar una imagen", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
else:
    uploaded_file = col2.camera_input("Tomar una foto con la cámara")

path = "imagen_user.jpg"

# Crear contenedores de imagen para asegurar alineación
with col1:
    col1_image_container1 = st.empty()
    col1_text_container1 = st.empty()
    col1_image_container2 = st.empty()
    col1_text_container2 = st.empty()

with col2:
    col2_image_container1 = st.empty()
    col2_text_container1 = st.empty()
    col2_image_container2 = st.empty()
    col2_text_container2 = st.empty()

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image.save(path)

    img_03MP = cv.resize(cv.imread(path)[..., ::-1], (1536, 2048))
    img = img_03MP
    img_normal, ref_white, mean, sample = sc.Normal(img, white_limit=240)

    col1_image_container1.image(ref_white, use_column_width=True, output_format='auto')
    col1_text_container1.markdown("<p class='centered-text'>Imagen del Usuario</p>", unsafe_allow_html=True)

    col2_image_container1.image(img_normal, use_column_width=True, output_format='auto')
    col2_text_container1.markdown("<p class='centered-text'>Imagen Procesada</p>", unsafe_allow_html=True)

    Lab = sc.RGB2Lab(img_normal)
    Malo, CafeMalo, Bueno, CafeBueno = sc.MaskLabV2(Lab, img_normal, sample, ((22, 99), (15, 100)))

    col1_image_container2.image(Bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col1_text_container2.markdown("<p class='centered-text'>Café bueno</p>", unsafe_allow_html=True)

    col2_image_container2.image(Malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col2_text_container2.markdown("<p class='centered-text'>Café malo</p>", unsafe_allow_html=True)

    num_prueba = len(st.session_state.results_list) + 1  # Obtener el número de prueba
    fecha_hora_actual = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtener la fecha y hora actual

    st.session_state.results_list.append({
        "#prueba": num_prueba,
        "Fecha y Hora": fecha_hora_actual,
        "% cafe bueno": str(CafeBueno)[:6],
        "% cafe malo": str(CafeMalo)[:6]
    })

    with col3:
        st.table(pd.DataFrame(st.session_state.results_list).style.set_properties(**{'text-align': 'center'}))

    # Agregar un botón para exportar la tabla como PDF
    if col3.button('Exportar a PDF'):
        pdf_filename = sc.exportar_a_pdf(pd.DataFrame(st.session_state.results_list))
        st.success(f"Tabla exportada como '{pdf_filename}'")
else:
    # Añadir un contenedor vacío para mantener la alineación cuando no hay imágenes
    col1_image_container1.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
    col2_image_container1.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
    col1_image_container2.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
    col2_image_container2.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
