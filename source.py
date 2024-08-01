import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import cv2 as cv
import spectral.io.envi as envi
from spectral import * 
from rembg import remove
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import base64
import os
import io



fold = lambda unfold_image,size: unfold_image.reshape(size)
read = lambda path: cv.imread(path)[...,::-1]



def load_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def __unfold__(image_rgb:np.array):

    size = tuple(image_rgb.shape)
    image_unfold = image_rgb.reshape(-1,3)

    return image_unfold,size

def Normal(img: np.ndarray, white_limit: int):
    image_fg = remove(img)
    data, features = __unfold__(img)

    std = data.std(axis=1)
    mean_std = np.mean(std)
    sigma = np.std(std)
    
    stdlim = mean_std + 3 * np.std(std <=  (0.5*sigma))
    mask_background = std <= stdlim

    background_reference = data[mask_background]
    background_reference_mean = background_reference.mean(axis=1)
    mask_white = background_reference_mean >= white_limit

    construction_data = np.zeros_like(data,dtype=np.float64)
    ref_white = np.copy(data)

    idx_foreground = image_fg[:, :, 3].reshape(-1) > 200
    construction_data[idx_foreground] = data[idx_foreground]

    mean = background_reference[mask_white].mean(axis=0)
    
    construction_data /= mean
    construction_data[construction_data > 1] = 1

    mask_background[mask_background==True] = mask_white
    ref_white[mask_background] = 0
    construction_data = construction_data.reshape(features)
    ref_white = ref_white.reshape(features)

    sample = np.count_nonzero(idx_foreground)

    return construction_data, ref_white, mean, idx_foreground


def RGB2Lab(img_rgb:np.ndarray):

    img_data,size = __unfold__(img_rgb)

    e =  216/24389

    gamma_correction = img_data[:,:]**(2.2)

    X = gamma_correction[:, 0] * 0.4124 + gamma_correction[:, 1] * 0.3576 + gamma_correction[:, 2] * 0.1805
    Y = gamma_correction[:, 0] * 0.2126 + gamma_correction[:, 1] * 0.7152 + gamma_correction[:, 2] * 0.0722
    Z = gamma_correction[:, 0] * 0.0193 + gamma_correction[:, 1] * 0.1192 + gamma_correction[:, 2] * 0.9505

    fx = (X/0.94811)
    fy = (Y/1)
    fz = (Z/1.07304)

    if fx.any() > e:
        fx = fx**(1/3)
    else:
        fx = ((903.3*fx)+16)/116

    if fy.any() > e:
        fy = fy**(1/3)
    else:
        fy = ((903.3*fy)+16)/116

    if fz.any() > e:
        fz = fz**(1/3)
    else:
        fz = ((903.3*fz)+16)/116

    a = (fx - fy) * 500
    b = (fy - fz) * 200
    L = (fy * 116) - 16
    L = np.clip(L,0,200)

    data_CLab = np.column_stack((L, a, b))

    return data_CLab


def MaskLabV2(img_Lab:np.ndarray,img_rgb:np.ndarray,mask_fg:np.ndarray,mask:tuple):

    mask_L, mask_a  = mask

    inf_L, sup_L = mask_L
    inf_a, sup_a = mask_a


    Lab_unfold,_  = __unfold__(img_Lab)
    RGB_unfold,_  = __unfold__(img_rgb)

    Lab_sample = np.zeros_like(Lab_unfold)
    RGB_sample = np.zeros_like(RGB_unfold)

    Lab_sample[mask_fg] = Lab_unfold[mask_fg]
    RGB_sample[mask_fg] = RGB_unfold[mask_fg]

    L, a, b = Lab_unfold[mask_fg][:,0],Lab_unfold[mask_fg][:,1],Lab_unfold[mask_fg][:,2]
    R, G, B = RGB_unfold[:,0],RGB_sample[:,1],RGB_sample[:,2]

    condition = np.logical_and

    mask_condition = condition(condition(L >= inf_L, L <= sup_L),condition(a >= inf_a, a <= sup_a))

    RGB_bad = np.zeros_like(RGB_unfold)
    RGB_good = np.zeros_like(RGB_unfold)

    Bad = RGB_bad[mask_fg]
    Bad[~mask_condition] = RGB_unfold[mask_fg][~mask_condition]
    RGB_bad[mask_fg] = Bad

    Good = RGB_good[mask_fg]
    Good[mask_condition] = RGB_unfold[mask_fg][mask_condition]
    RGB_good[mask_fg] = Good

    RGB_bad = fold(RGB_bad,_)
    RGB_good = fold(RGB_good,_)
    
    PGood =(RGB_good[:,:,0][RGB_good[:,:,0]!=0].shape[0]/mask_fg[mask_fg==True].shape[0])*100
    PBad = (RGB_bad[:,:,0][RGB_bad[:,:,0]!=0].shape[0]/mask_fg[mask_fg==True].shape[0])*100

    return RGB_bad,PBad, RGB_good, PGood


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


