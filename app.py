import streamlit as st
from PIL import Image
import pandas as pd
import source as sc
import cv2 as cv
import os

st.set_page_config(layout="wide")  # Configurar el ancho de la página

# Obtener la ruta del directorio actual (donde se encuentra el archivo principal)
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, r"logo2.png")  # rutas de los logos

# CSS para personalizar el título, los radio buttons y hacer que el diseño sea responsivo
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
        align-items: center;
        justify-content: center;
        gap: 10px;  /* Ajusta el espacio entre la imagen y los radio buttons */    
    }
    .image-container img {
        max-width: 100%;
        height: auto;
    }
    .horizontal-radio {
        display: flex;
        flex-direction: column; /* Asegura que los radio buttons estén uno debajo del otro */
        justify-content: center;
        margin: 0;  /* Asegura que el margen sea mínimo */
        font-size: 24px; /* Tamaño de la fuente */
    }
    .horizontal-radio label {
        margin: 0 20px;
        font-size: 24px; /* Tamaño del texto */
        display: flex;
        align-items: center;
    }
    .horizontal-radio input[type="radio"] {
        margin-right: 10px; /* Espacio entre el radio button y el texto */
        width: 20px; /* Tamaño del radio button */
        height: 20px; /* Tamaño del radio button */
    }
    .camera-container {
        width: 100%; /* Asegura que la cámara use el ancho completo */
        display: flex;
        justify-content: center;
    }
    .camera-container video {
        width: 100% !important; /* Asegura que el video use el ancho completo */
    }
    @media (max-width: 600px) {
        .title {
            font-size: 48px;
        }
        .column-container {
            flex-direction: column;
        }
        .column {
            width: 100% !important;
            padding: 0;
        .image-container {
            flex-direction: column;
            gap: 10px; /* Ajusta el espacio en vistas móviles */
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

image_base64 = sc.load_image(ruta_logo)

# HTML y CSS para el título y la imagen
html_content = f"""
    <style>
    body {{
        margin-top: 0px;
        padding-top: 0px;
    }}
    .title {{
        text-align: center;
        font-weight: bold;
        font-size: 22px;  /* Tamaño de la letra */
        font-family: 'Arial', sans-serif;
        margin-top: 0;  /* Asegura que el título quede bien arriba */
        margin-bottom: 0px;  /* Espacio mínimo entre el título y la imagen */
        padding-top: 0px;
    }}
    .image-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;  /* Espacio entre la imagen y el radio button */
    }}
    .image-container img {{
        width: 200px;  
        height: auto;  
    }}
    .radio-container {{
        display: flex;
        flex-direction: column;  /* Coloca los radio buttons verticalmente */
        justify-content: center;
        margin-top: 0px;  /* Espacio mínimo entre la imagen y el radio button */
    }}

    </style>
    <h1 class="title">Clasificador de café cereza</h1>
    <div class="image-container">
        <img src="data:image/png;base64,{image_base64}" alt="Descripción de la imagen">
        <div class="radio-container">
            <label>
                <input type="radio" name="method" value="Tomar foto" checked>
                Tomar foto
            </label>
            <label>
                <input type="radio" name="method" value="Cargar imagen">
                Cargar imagen
            </label>
        </div>
    </div>
    """


# Mostrar el contenido HTML en Streamlit
st.markdown(html_content, unsafe_allow_html=True)