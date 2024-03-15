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
import os


fold = lambda unfold_image,size: unfold_image.reshape(size)
read = lambda path: cv.imread(path)[...,::-1]


def read_img(path:str):

    image_bgr = cv.imread(path)
    image_rgb = image_bgr[:,:,::-1]

    return image_rgb

def __unfold__(image_rgb:np.array):

    size = tuple(image_rgb.shape)
    image_unfold = image_rgb.reshape(-1,3)

    return image_unfold,size

def __fold__(unfold_image:np.array,size:tuple):

    img_fold = unfold_image.reshape(size)
    return img_fold

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


def RGB2Labv2(img_rgb: np.ndarray):

    img_data,size = __unfold__(img_rgb)
    gamma_correction = img_data ** 2.2

    xyz_linear = np.dot(gamma_correction, np.array([[0.4124, 0.3576, 0.1805],
                                                     [0.2126, 0.7152, 0.0722],
                                                     [0.0193, 0.1192, 0.9505]]).T)

    xyz_normalized = xyz_linear / np.array([0.950456, 1.0, 1.088754])

  
    epsilon = 216 / 24389
    linear_condition = xyz_normalized > epsilon
    xyz_final = np.where(linear_condition, xyz_normalized ** (1 / 3), (xyz_normalized * 903.3 + 16) / 116)

    L = 116 * xyz_final[:, 1] - 16
    L = np.clip(L, 0, 100)
    a = 500 * (xyz_final[:, 0] - xyz_final[:, 1])
    b = 200 * (xyz_final[:, 1] - xyz_final[:, 2])

    Lab = fold(np.column_stack((L, a, b)),size)

    return Lab


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

def Lab2Lch(img_Lab):

    Lab,size = __unfold__(img_Lab)

    L, a, b = Lab[:, 0], Lab[:, 1], Lab[:, 2]

    c = np.sqrt(a**2 + b**2)
    h = np.arctan2(b, a) * (180 / np.pi)
    h[h < 0] += 360
    
    Lch = fold(np.column_stack((L, c, h)),size)
    return Lch




def export_img(dir:str,img_normal:np.ndarray):


    img_normal_unfold,size = __unfold__(img_normal)

    Lab_unfold = RGB2Lab(img_normal_unfold)
    Lch_unfold = Lab2Lch(Lab_unfold)

    Lab = Lab_unfold.reshape(size)
    Lch = Lch_unfold.reshape(size)

    L = Lab[:,:,0]
    c = Lch[:,:,1]
    h = Lch[:,:,2]
    a = Lab[:,:,1]
    b = Lab[:,:,2]

    data = np.stack((L,a,b,c,h),axis= 2)

    with open(dir + '.raw','wb') as f:
        data.tofile(f)

    hdr_metadata = {
        'lines': data.shape[1],
        'samples': data.shape[2],
        'bands': data.shape[0],
        'data type': str(data.dtype),
        'interleave': 'bsq',
        'byte order': 0,
        'band names': ['L', 'A', 'B','C','H'],
        'descriptions': ['Brillo', 'A','B','Croma', 'Tono'],
        'data ignore value': -999.0
        }
    hdr_path_out = dir + ".hdr"
    envi.save_image(hdr_path_out, data, metadata=hdr_metadata)


def MaskLab(img: np.ndarray, img_rgb: np.ndarray, LAB: str = "L", mask: tuple = (0, 150)):
    img_ = np.zeros_like(img)
    img_show = np.zeros_like(img)

    inf, sup = mask
    L, a, b = img[:,:,0], img[:,:,1], img[:,:,2]

    condition = np.logical_and

    if LAB == "L":
        mask_condition = condition(L >= inf, L <= sup)
    elif LAB == "a":
        mask_condition = condition(a >= inf, a <= sup)
    elif LAB == "b":
        mask_condition = condition(b >= inf, b <= sup)
    else:
        print("valor de Lab invalido")
        return None, None

    img_[:, :, 0][mask_condition] = L[mask_condition]
    img_[:, :, 1][mask_condition] = a[mask_condition]
    img_[:, :, 2][mask_condition] = b[mask_condition]

    img_show[:, :, 0][mask_condition] = img_rgb[:, :, 0][mask_condition]
    img_show[:, :, 1][mask_condition] = img_rgb[:, :, 1][mask_condition]
    img_show[:, :, 2][mask_condition] = img_rgb[:, :, 2][mask_condition]

    return img_, img_show


"""_______________________________________________________________________________________"""



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


def test_unfold(img_normal):

    Lab_unfold = RGB2Lab(img_normal.reshape(-1,3))
    Lch_unfold = Lab2Lch(Lab_unfold)

    Lab = Lab_unfold.reshape(img_normal.shape)
    Lch = Lch_unfold.reshape(img_normal.shape)

    return Lab


def test_mask(Lab, img_normal):
    # MASCARA PARA VERDE
    MaskL_Verde,img_maskL_Verde = MaskLab(Lab,img_normal,"L",(50,100))
    Maska_verde,img_maska_Verde = MaskLab(MaskL_Verde,img_maskL_Verde,"a",(-50,-10))

    # MASCARA PARA PINTON
    MaskL_Pinton,img_maskL_Pinton = MaskLab(Lab,img_normal,"L",(61,99.9))
    Maska_Pinton,img_maska_Pinton = MaskLab(MaskL_Pinton,img_maskL_Pinton,"a",(-9,25))

    # MASCARA PARA MADURO
    MaskL_Maduro,img_maskL_Maduro = MaskLab(Lab,img_normal,"L",(20,99))
    Maska_Maduro,img_maska_Maduro = MaskLab(MaskL_Maduro,img_maskL_Maduro,"a",(15,100))

    # MASCARA PARA SOBREMADURO
    MaskL_SMaduro,img_maskL_SMaduro = MaskLab(Lab,img_normal,"L",(0,60))
    Maska_SMaduro,img_maska_SMaudro = MaskLab(MaskL_SMaduro,img_maskL_SMaduro,"a",(-10,15))

    return Maska_verde, img_maska_Verde, Maska_Pinton, img_maska_Pinton,  Maska_Maduro, img_maska_Maduro,  Maska_SMaduro, img_maska_SMaudro


def test_result(Maska_verde, img_maska_Verde, Maska_Pinton,img_maska_Pinton, Maska_Maduro, img_maska_Maduro,  Maska_SMaduro, img_maska_SMaudro, sample ):


    img_malo = np.zeros_like(Maska_verde.reshape(-1,3))
    img_bueno = np.zeros_like(Maska_Pinton.reshape(-1,3))
    img_suma = np.zeros_like(Maska_Maduro.reshape(-1,3))


    porcentaje_Verde = (Maska_verde[:,:,0][Maska_verde[:,:,0]!=0].shape[0]/sample)*100
    porcentaje_Pinton = (Maska_Pinton[:,:,0][Maska_Pinton[:,:,0]!=0].shape[0]/sample)*100
    porcentaje_Maduro = (Maska_Maduro[:,:,0][Maska_Maduro[:,:,0]!=0].shape[0]/sample)*100
    porcentaje_SMaduro = (Maska_SMaduro[:,:,0][Maska_SMaduro[:,:,0]!=0].shape[0]/sample)*100

    # Suma de las máscaras
    idx_verde = np.where(img_maska_Verde.reshape(-1,3)!=0)[0]
    idx_Pinton = np.where(img_maska_Pinton.reshape(-1,3)!=0)[0]
    idx_Maduro = np.where(Maska_Maduro.reshape(-1,3)!=0)[0]
    idx_SMaduro = np.where(Maska_SMaduro.reshape(-1,3)!=0)[0]

    #SUMA TOTAL
    img_suma[idx_verde] = img_maska_Verde.reshape(-1,3)[idx_verde]
    img_suma[idx_Pinton] = img_maska_Pinton.reshape(-1,3)[idx_Pinton]
    img_suma[idx_Maduro] = img_maska_Maduro.reshape(-1,3)[idx_Maduro]
    img_suma[idx_SMaduro] = img_maska_SMaudro.reshape(-1,3)[idx_SMaduro]

    #SUMA CAFE BUENO
    img_bueno[idx_Maduro] = img_maska_Maduro.reshape(-1,3)[idx_Maduro]

    #SUMA CAFE MALO
    img_malo[idx_Pinton] = img_maska_Pinton.reshape(-1,3)[idx_Pinton]
    img_malo[idx_verde] = img_maska_Verde.reshape(-1,3)[idx_verde]
    img_malo[idx_SMaduro] = img_maska_SMaudro.reshape(-1,3)[idx_SMaduro]

    #suma de los porcentajes
    porcentaje_suma = porcentaje_SMaduro + porcentaje_Maduro + porcentaje_Verde + porcentaje_Pinton
    porcentaje_bueno = porcentaje_Maduro 
    porcentaje_malo = porcentaje_Pinton + porcentaje_Verde + porcentaje_SMaduro

    return porcentaje_suma, porcentaje_bueno, porcentaje_malo, img_bueno, img_malo


def exportar_a_pdf(dataframe):
    # Crear un archivo PDF
    pdf_filename = "tabla_resultados.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)

    # Convertir el DataFrame a una lista de listas
    data = [list(dataframe.columns)] + dataframe.values.tolist()

    # Crear una tabla a partir de los datos
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    # Aplicar estilo a la tabla
    table.setStyle(style)

    # Crear la lista de elementos a añadir al PDF
    elements = [table]

    # Generar el PDF
    pdf.build(elements)

    return pdf_filename


"""
plt.subplot(1, 3, 2)
plt.title(f"Café Bueno: {(porcentaje_bueno/porcentaje_suma)*100:.2f}%")
plt.imshow(img_bueno.reshape(img_normal.shape))
plt.axis('off')

plt.subplot(1, 3, 3)
plt.title(f"Café Malo: {(porcentaje_malo/porcentaje_suma)*100:.2f}%")
plt.imshow(img_malo.reshape(img_normal.shape))
plt.axis('off')
"""