import streamlit as st
import pandas as pd
from PIL import Image
import source as sc
import numpy as np

# Título centrado en la página
st.markdown("<h1 style='text-align: center;'>Bienvenidos a la aplicación para clasificar café</h1>", unsafe_allow_html=True)

# Crear o cargar el DataFrame para almacenar los resultados de las pruebas
if 'results_list' not in st.session_state:
    st.session_state.results_list = []


# Cargar imagen y mostrarla en un solo clic
uploaded_file = st.file_uploader("")
path="imagen_user.jpg"



# Mostrar imagen centrada si se ha cargado
if uploaded_file is not None:
    
    col1, col2 = st.columns(2)
    
    image = Image.open(uploaded_file)
    image_user = image.save(path)  
    img_normal,ref_white,mean,sample = sc.Normal(sc.read_img(path),white_limit=240)
    
    
    col1.image(uploaded_file, use_column_width=True, output_format='auto')
    col1.markdown("<p style='text-align: center; font-size: 18px; color: white; font-weight: bold; font-style: italic;'>Imagen del Usuario</p>", unsafe_allow_html=True)

    col2.image(img_normal, use_column_width=True, output_format='auto')
    col2.markdown("<p style='text-align: center; font-size: 18px; color: white; font-weight: bold; font-style: italic;'>Imagen Procesada</p>", unsafe_allow_html=True)

    
    #st.image(img_normal, use_column_width=True, output_format='auto')
    #st.markdown("<p style='text-align: center", unsafe_allow_html=True)

    Lab = sc.test_unfold(img_normal)
    Mas_V, img_mas_V, Mas_P, img_mas_P, Mas_M, img_ma_M, Mas_SM, img_ma_SM = sc.test_mask(Lab, img_normal)
    porcentaje_suma, porcentaje_bueno, porcentaje_malo, img_bueno, img_malo = sc.test_result(Mas_V, img_mas_V, Mas_P, img_mas_P, Mas_M, img_ma_M, Mas_SM, img_ma_SM, sample)         

    col1.image(img_bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col1.markdown("<p style='text-align: center; font-size: 18px; color: white; font-weight: bold; font-style: italic;'>Café bueno</p>", unsafe_allow_html=True)

    col2.image(img_malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col2.markdown("<p style='text-align: center; font-size: 18px; color: white; font-weight: bold; font-style: italic;'>Café malo</p>", unsafe_allow_html=True)

    # Obtener el número de prueba
    num_prueba = len(st.session_state.results_list) + 1

    # Obtener la fecha y hora actual
    fecha_hora_actual = pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')

    st.session_state.results_list.append({
        "#prueba": num_prueba,
        "Fecha y Hora": fecha_hora_actual,
        "%cafe bueno":round((porcentaje_bueno/porcentaje_suma)*100,2),
        "%cafe malo": round((porcentaje_malo/porcentaje_suma)*100,2)
    })

    # Mostrar la tabla actualizada con st.table
    st.table(pd.DataFrame(st.session_state.results_list))      



