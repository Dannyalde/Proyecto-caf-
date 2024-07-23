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

# CSS para personalizar el título y hacer que el diseño sea responsivo
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 64px;
        margin-bottom: 40px;
    }
    .column-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .column {
        flex: 1;
        padding: 10px;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .image-container img {
        max-width: 100%;
        height: auto;
    }
    @media (max-width: 600px) {
        .column-container {
            flex-direction: column;
        }
        .column {
            width: 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título en la parte superior
st.markdown("<h1 class='title'>Bienvenidos a la aplicación para clasificar café</h1>", unsafe_allow_html=True)

# Crear las columnas para los logos
col1, col2 = st.columns(2)

with col1:
    st.image(logo_izquierdo, use_column_width=True)

with col2:
    st.image(logo_derecho, use_column_width=True)

# El resto del código está comentado para trabajarlo paso a paso

# if 'results_list' not in st.session_state:  # Crear el DataFrame para almacenar los resultados de las pruebas
#     st.session_state.results_list = []

# Seleccionar método de carga de imagen
# method = st.radio("Selecciona un método para cargar la imagen", ["Cargar imagen desde el computador", "Tomar una foto con la cámara"])

# uploaded_file = None
# if method == "Cargar imagen desde el computador":
#     uploaded_file = st.file_uploader("Cargar una imagen", type=["jpg", "jpeg", "png"])
# else:
#     uploaded_file = st.camera_input("Tomar una foto con la cámara")

# path = "imagen_user.jpg"

# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     image.save(path)

#     img_03MP = cv.resize(cv.imread(path)[..., ::-1], (1536, 2048))
#     img = img_03MP
#     img_normal, ref_white, mean, sample = sc.Normal(img, white_limit=240)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.image(ref_white, use_column_width=True, output_format='auto')
#         st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Imagen del Usuario</p>", unsafe_allow_html=True)

#     with col2:
#         st.image(img_normal, use_column_width=True, output_format='auto')
#         st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Imagen Procesada</p>", unsafe_allow_html=True)

#     Lab = sc.RGB2Lab(img_normal)
#     Malo, CafeMalo, Bueno, CafeBueno = sc.MaskLabV2(Lab, img_normal, sample, ((22, 99), (15, 100)))

#     with col1:
#         st.image(Bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
#         st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

#     with col2:
#         st.image(Malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')
#         st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café malo</p>", unsafe_allow_html=True)

#     num_prueba = len(st.session_state.results_list) + 1  # Obtener el número de prueba
#     fecha_hora_actual = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtener la fecha y hora actual

#     st.session_state.results_list.append({
#         "#prueba": num_prueba,
#         "Fecha y Hora": fecha_hora_actual,
#         "% cafe bueno": str(CafeBueno)[:6],
#         "% cafe malo": str(CafeMalo)[:6]
#     })

#     st.table(pd.DataFrame(st.session_state.results_list).style.set_properties(**{'text-align': 'center'}))

#     # Agregar un botón para exportar la tabla como PDF
#     if st.button('Exportar a PDF'):
#         pdf_filename = sc.exportar_a_pdf(pd.DataFrame(st.session_state.results_list))
#         st.success(f"Tabla exportada como '{pdf_filename}'")

