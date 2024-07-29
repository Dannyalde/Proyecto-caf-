import streamlit as st
from PIL import Image
import base64
import os

# Configurar la página
st.set_page_config(layout="wide")

# Obtener la ruta del directorio actual
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(directorio_actual, r"logo2.png")

def load_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = load_image(ruta_logo)

# CSS para la página
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        margin-bottom: 20px;
    }
    .image-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }
    .image-container img {
        width: 200px;
        height: auto;
    }
    .selectbox-container {
        display: flex;
        flex-direction: column;
        margin: 0;
    }
    .selectbox-container select {
        font-size: 16px;
        margin: 5px 0;
    }
    @media (max-width: 600px) {
        .title {
            font-size: 28px;
        }
        .image-container {
            flex-direction: column;
            gap: 10px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Mostrar el título y la imagen
st.markdown(f'<h1 class="title">Clasificador de café cereza</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="image-container"><img src="data:image/png;base64,{image_base64}" alt="Descripción de la imagen"></div>', unsafe_allow_html=True)

# Selección de opción usando Streamlit
selected_option = st.selectbox(
    'Seleccionar opción:',
    ['Tomar foto', 'Cargar imagen'],
    index=0  # Establecer "Tomar foto" como opción por defecto
)

# Almacenar la selección en el estado de sesión
st.session_state['selected_option'] = selected_option

# Mostrar la interfaz según la selección
if selected_option == "Cargar imagen":
    uploaded_file = st.file_uploader("Sube tu imagen", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption='Imagen cargada')
else:
    uploaded_file = st.camera_input("Toma una foto")
    if uploaded_file:
        st.image(uploaded_file, caption='Foto tomada')

# Mostrar la selección actual
st.write(f"Selección actual: {selected_option}")
