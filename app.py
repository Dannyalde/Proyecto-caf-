import streamlit as st
import pandas as pd
from PIL import Image
import source as sc
import numpy as np
import cv2 as cv
import os

st.set_page_config(layout="wide")                                         # Configurar el ancho de la página
directorio_actual = os.path.dirname(os.path.abspath(__file__))            # Obtener la ruta del directorio actual (donde se encuentra el archivo principal)  
ruta_logo_izquierdo = os.path.join(directorio_actual, r"logo_cafe.png")   # rutas de los logos
ruta_logo_derecho = os.path.join(directorio_actual, r"logoUA.png")

logo_izquierdo = Image.open(ruta_logo_izquierdo) # Cargar las imágenes
logo_derecho = Image.open(ruta_logo_derecho)

ancho_columna_izquierda = 0.35
ancho_columna_centro = 0.35
ancho_columna_derecha = 0.5

col1, col2, col3 = st.columns([ancho_columna_izquierda, ancho_columna_centro, ancho_columna_derecha]) # Crear utres columnas 
col1.image(logo_izquierdo, use_column_width=True, width=40) # Mostrar logotipo izquierdo en la columna 1
col3.image(logo_derecho, use_column_width=True, width=100)  # Mostrar logotipo derecho en la columna 3

# Título centrado en la página
col2.markdown("<h1 style='text-align: center; font-size: 30px;'>Bienvenidos a la aplicación para clasificar café</h1>", unsafe_allow_html=True)

if 'results_list' not in st.session_state:  # Crear el DataFrame para almacenar los resultados de las pruebas
    st.session_state.results_list = []

# Seleccionar método de carga de imagen
method = col2.radio(" ", ["Cargar imagen desde el computador", "Tomar una foto con la cámara"])

uploaded_file = None
if method == "Cargar imagen desde el computador":
    uploaded_file = col2.file_uploader("Cargar una imagen", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
else:
    uploaded_file = col2.camera_input("Tomar una foto con la cámara")

path = "imagen_user.jpg"

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    image.save(path)

    img_03MP = cv.resize(cv.imread(path)[..., ::-1], (1536, 2048))
    img = img_03MP
    img_normal, ref_white, mean, sample = sc.Normal(img, white_limit=240)

    col1.image(ref_white, use_column_width=True, output_format='auto')
    col1.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Imagen del Usuario</p>", unsafe_allow_html=True)

    col2.image(img_normal, use_column_width=True, output_format='auto')
    col2.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Imagen Procesada</p>", unsafe_allow_html=True)

    Lab = sc.RGB2Lab(img_normal)
    Malo, CafeMalo, Bueno, CafeBueno = sc.MaskLabV2(Lab, img_normal, sample, ((22, 99), (15, 100)))

    col1.image(Bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col1.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

    col2.image(Malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col2.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café malo</p>", unsafe_allow_html=True)

    num_prueba = len(st.session_state.results_list) + 1                       # Obtener el número de prueba
    fecha_hora_actual = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')      # Obtener la fecha y hora actual

    st.session_state.results_list.append({
        "#prueba": num_prueba,
        "Fecha y Hora": fecha_hora_actual,
        "% cafe bueno": str(CafeBueno)[:6],
        "% cafe malo": str(CafeMalo)[:6]
    })

    col3.table(pd.DataFrame(st.session_state.results_list).style.set_properties(**{'text-align': 'center'}))

    # Agregar un botón para exportar la tabla como PDF
    if col3.button('Exportar a PDF'):
        pdf_filename = sc.exportar_a_pdf(pd.DataFrame(st.session_state.results_list))
        st.success(f"Tabla exportada como '{pdf_filename}'")



