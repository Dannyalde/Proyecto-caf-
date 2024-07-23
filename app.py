import streamlit as st
from PIL import Image
import pandas as pd
import source as sc
import cv2 as cv
import os

st.set_page_config(layout="wide")  # Configurar el ancho de la página

# Obtener la ruta del directorio actual (donde se encuentra el archivo principal)
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo_izquierdo = os.path.join(directorio_actual, r"logo_cafe.png")  # rutas de los logos
ruta_logo_derecho = os.path.join(directorio_actual, r"logoUA.png")

# Cargar las imágenes
logo_izquierdo = Image.open(ruta_logo_izquierdo)
logo_derecho = Image.open(ruta_logo_derecho)

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
        justify-content: center;
        align-items: center;
    }
    .image-container img {
        max-width: 100%;
        height: auto;
    }
    .horizontal-radio {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 40px;
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
        }
        .horizontal-radio {
            flex-direction: column;
        }
        .horizontal-radio label {
            margin: 10px 0;
        }
        .camera-container {
            width: 100%;
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

# Crear el radio button de manera horizontal
st.markdown("<div class='horizontal-radio'>", unsafe_allow_html=True)
method = st.radio("", ["Tomar una foto con la cámara", "Cargar imagen"], index=0, horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

show_image = False

# Seleccionar método de carga de imagen en una sola columna
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


if uploaded_file is not None:

    image = Image.open(uploaded_file) 
    path = "imagen_user.jpg"
    image.save(path)

    # Procesar la imagen
    img_03MP = cv.resize(cv.imread(path)[..., ::-1], (1536, 2048))
    img = img_03MP
    img_normal, ref_white, mean, sample = sc.Normal(img, white_limit=240)

    col1, col2 = st.columns(2)
    Lab = sc.RGB2Lab(img_normal)
    Malo, CafeMalo, Bueno, CafeBueno = sc.MaskLabV2(Lab, img_normal, sample, ((22, 99), (15, 100)))

    col1, col2 = st.columns(2)

    with col1:
        st.image(Bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
        st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

    with col2:
        st.image(Malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')
        st.markdown("<p style='text-align: center; font-size: 18px; color: black; font-weight: bold; font-style: italic;'>Café malo</p>", unsafe_allow_html=True)


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
    st.markdown("<h2 style='text-align: center;'>Resultados de las pruebas</h2>", unsafe_allow_html=True)
    st.table(pd.DataFrame(st.session_state.results_list).style.set_properties(**{'text-align': 'center'}))

    # Agregar un botón para exportar la tabla como PDF
    if st.button('Exportar a PDF'):
        pdf_filename = sc.exportar_a_pdf(pd.DataFrame(st.session_state.results_list))
        st.success(f"Tabla exportada como '{pdf_filename}'")
