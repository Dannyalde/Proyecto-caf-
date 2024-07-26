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
                <input type="radio" name="method" value="Tomar una foto con la cámara" checked>
                Tomar una foto con la cámara
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
method = st.radio("", ["Tomar una foto con la cámara", "Cargar imagen"], index=0, horizontal=False)



#st.markdown('<div style="font-family:Arial; font-size:20px; font-weight:bold;">Clasificador de café cereza</div>', unsafe_allow_html=True)
#st.image(logo)


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
