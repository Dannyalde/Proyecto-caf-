import streamlit as st
from PIL import Image
import source as sc

# Título centrado en la página
st.markdown("<h1 style='text-align: center;'>Bienvenidos a la aplicación para clasificar café</h1>", unsafe_allow_html=True)

# Cargar imagen y mostrarla en un solo clic
uploaded_file = st.file_uploader("")
path="imagen_user.jpg"



# Mostrar imagen centrada si se ha cargado
if uploaded_file is not None:
    
    image = Image.open(uploaded_file)
    image_user = image.save(path)    
    img_normal,ref_white,mean,sample = sc.Normal(sc.read_img(path),white_limit=240)
    st.image(img_normal, use_column_width=True, output_format='auto')
    st.markdown("<p style='text-align: center", unsafe_allow_html=True)

    Lab = sc.test_unfold(img_normal)
    Mas_V, img_mas_V, Mas_P, img_mas_P, Mas_M, img_ma_M, Mas_SM, img_ma_SM = sc.test_mask(Lab, img_normal)
    porcentaje_suma, porcentaje_bueno, porcentaje_malo, img_bueno, img_malo = sc.test_result(Mas_V, img_mas_V, Mas_P, img_mas_P, Mas_M, img_ma_M, Mas_SM, img_ma_SM, sample)         


    col1, col2 = st.columns(2)
    #col1.image(img_bueno, caption="Imagen Izquierda", use_column_width=True, output_format='auto')
    col1.image(img_bueno.reshape(img_normal.shape), use_column_width=True, output_format='auto')
    col2.image(img_malo.reshape(img_normal.shape), use_column_width=True, output_format='auto')



    




