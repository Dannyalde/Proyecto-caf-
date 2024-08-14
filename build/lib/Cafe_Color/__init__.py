# Importar las clases principales
from .read_features import Image
from .preprocessing import Preprocess
from .segmentation import ColorSegmentation

# Importar las constantes

from .constans import RGB_LAB_MATRIX_D65,XYZ_D65_STANDAR_ILUMINATION,EPSILON

# Definir metadatos del paquete
__version__ = '1.0.0'
__author__ = 'Jorge A. Ramírez, Jose D. Ardila, Andrés F. Cerón'
__email__ = 'jorge.ramirez@profesores.uamerica.edu.co'
__description__ = 'Calsificación de Café'

# Definir qué se exporta cuando se importa el paquete
__all__ = [
    'Image',
    'Preprocess',
    'ColorSegmentation',
    'RGB_LAB_MATRIX_D65',
    'XYZ_D65_STANDAR_ILUMINATION',
    'EPSILON'
]
