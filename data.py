from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from PIL import Image
import streamlit as st
import logging
import base64
import io

# Configurar el registro de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def exportar_a_pdf(dataframe):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Convertir el DataFrame a una lista de listas
    data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    elements = [table]
    pdf.build(elements)

    buffer.seek(0)
    return buffer.read()


def load_image(image_path):
    """Carga una imagen y la convierte a base64."""
    try:
        with open(image_path, "rb") as img_file:            
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error al cargar la imagen: {e}")
        logger.error(f"Error al cargar la imagen: {e}")
        return ""
    

def reducir_tamano_imagen(image_path, max_width=1024):
    # Abrir la imagen
    img = Image.open(image_path)
    
    # Redimensionar la imagen si su ancho es mayor al límite
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)  # Usar LANCZOS para redimensionado
            
    # Guardar la imagen en un buffer de memoria
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=85)  # Ajusta la calidad si es necesario
    buffer.seek(0)  # Esto se asegura de que estemos al inicio del archivo en el buffer

    return buffer