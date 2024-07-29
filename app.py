import streamlit as st
from PIL import Image
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

st.markdown("""
    <style>
    .stRadio [role=radiogroup]{
        align-items: center;
        justify-content: center;
    }
    </style>
""",unsafe_allow_html=True)

options = ["An option", "🦈", "Another option", "🎨", "x²"]

"# 🎯 Center align elements"
st.radio("Select an option", options=options, horizontal=True)



st.markdown(
    """
    <style>
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
        margin: 0px 0; /* Reduce el espacio entre la imagen y los radio buttons */
    }
    .image-container img {
        width: 50vw; /* Ajusta el tamaño de la imagen para dispositivos móviles */
        height: auto;
    }
    .radio-buttons-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0px 0; /* Reduce el espacio entre los radio buttons y el siguiente contenido */
    }
    .uploader-container {
        margin-top: 0px; /* Reduce el espacio entre los radio buttons y el uploader */
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

# Mostrar la interfaz según la selección
st.markdown('<div class="uploader-container">', unsafe_allow_html=True)
if method == "Cargar imagen":
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            st.image(uploaded_file, use_column_width=True)
        except Exception as e:
            st.error(f"Error al mostrar la imagen: {e}")
else:
    uploaded_file = st.camera_input("")
    if uploaded_file:
        try:
            st.image(uploaded_file, use_column_width=True)
        except Exception as e:
            st.error(f"Error al mostrar la foto: {e}")
st.markdown('</div>', unsafe_allow_html=True)
