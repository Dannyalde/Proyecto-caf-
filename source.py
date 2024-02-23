import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import cv2 as cv
import spectral.io.envi as envi
from spectral import * 
from rembg import remove


def read_img(path:str):

    image_bgr = cv.imread(path)
    image_rgb = image_bgr[:,:,::-1]

    return image_rgb

def unfold(image_rgb:np.array):

    size = tuple(image_rgb.shape)
    image_unfold = image_rgb.reshape(-1,3)

    return image_unfold, size

def Normal(img:np.ndarray,white_limit:int):


    image_fg = remove(img)
    data, features = unfold(img)
    
    std = data.std(1)
    hist, bin_edges = np.histogram(std,bins = 50)
    bin_centers = (bin_edges[:-1] + bin_edges[1:])/2
    sorted_idx = np.argsort(hist)
    max_idx = sorted_idx[-1]
    
    mean_hist = bin_centers[max_idx]
    sigma = np.std(std)

    sigma_idx = np.where(std <= mean_hist + (0.5*sigma))
    sigma_filt = np.std(std[sigma_idx])
    stdlim = mean_hist + 3*sigma_filt

    idx_background = np.where(std <= stdlim)[0]
    background_reference = data[idx_background]
    background_reference_mean = background_reference.mean(1)
    white_idx = np.where(background_reference_mean >= white_limit)[0]
    white_reference =  background_reference[white_idx]
    mean = white_reference.mean(0)

    construction_data = np.zeros_like(data)
    ref_white = np.copy(data)

    idx_ = np.where(image_fg[:,:,3].reshape(-1) > 200)
    construction_data[idx_] = data[idx_]

    construction_data = construction_data/mean
    np.place(construction_data, construction_data > 1,1)

    ref_white[idx_background[white_idx]] = np.array([0,0,0])
    construction_data = np.reshape(construction_data,features)
    ref_white = np.reshape(ref_white,features)
    sample = idx_[0].shape[0]
    return construction_data, ref_white, mean, sample

def RGB2Lab(img_data:np.ndarray):


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

def Lab2Lch(Lab):

    L = Lab[:,0]
    a = Lab[:,1]
    b = Lab[:,2]

    c = ((a**2)+(b**2))**(1/2)
    h = np.arctan2(b,a)*(180/np.pi)
    h[h < 0] += 360

    data_CLch = np.column_stack((L, c, h))
    
    return  data_CLch

def export_img(dir:str,img_normal:np.ndarray):


    img_normal_unfold,size = unfold(img_normal)

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

def MaskLab(img:np.ndarray,img_rgb:np.ndarray,LAB="L",mask=(0,150)):

    img_ = np.zeros_like(img)
    img_show = np.zeros_like(img)

    inf,sup = mask

    L = img[:,:,0]
    a = img[:,:,1]
    b = img[:,:,2]

    if LAB == "L":
        #idx = [np.logical_and(L>=inf,L<=sup)].shape[0]
        img_[:,:,0][np.logical_and(L>=inf,L<=sup)] = L[np.logical_and(L>=inf,L<=sup)]
        img_[:,:,1][np.logical_and(L>=inf,L<=sup)] = a[np.logical_and(L>=inf,L<=sup)]
        img_[:,:,2][np.logical_and(L>=inf,L<=sup)] = b[np.logical_and(L>=inf,L<=sup)]
        
        img_show[:,:,0][np.logical_and(L>=inf,L<=sup)] = img_rgb[:,:,0][np.logical_and(L>=inf,L<=sup)]
        img_show[:,:,1][np.logical_and(L>=inf,L<=sup)] = img_rgb[:,:,1][np.logical_and(L>=inf,L<=sup)]
        img_show[:,:,2][np.logical_and(L>=inf,L<=sup)] = img_rgb[:,:,2][np.logical_and(L>=inf,L<=sup)]

        return img_,img_show
    
    if LAB == "a":

        img_[:,:,0][np.logical_and(a>=inf,a<=sup)] = L[np.logical_and(a>=inf,a<=sup)]
        img_[:,:,1][np.logical_and(a>=inf,a<=sup)] = a[np.logical_and(a>=inf,a<=sup)]
        img_[:,:,2][np.logical_and(a>=inf,a<=sup)] = b[np.logical_and(a>=inf,a<=sup)]

        img_show[:,:,0][np.logical_and(a>=inf,a<=sup)] = img_rgb[:,:,0][np.logical_and(a>=inf,a<=sup)]
        img_show[:,:,1][np.logical_and(a>=inf,a<=sup)] = img_rgb[:,:,1][np.logical_and(a>=inf,a<=sup)]
        img_show[:,:,2][np.logical_and(a>=inf,a<=sup)] = img_rgb[:,:,2][np.logical_and(a>=inf,a<=sup)]

        return img_,img_show
    
    if LAB == "b":

        img_[:,:,0][np.logical_and(b>=inf,b<=sup)] = L[np.logical_and(b>=inf,b<=sup)]
        img_[:,:,1][np.logical_and(b>=inf,b<=sup)] = a[np.logical_and(b>=inf,b<=sup)]
        img_[:,:,2][np.logical_and(b>=inf,b<=sup)] = b[np.logical_and(b>=inf,b<=sup)]

        img_show[:,:,0][np.logical_and(b>=inf,b<=sup)] = img_rgb[:,:,0][np.logical_and(b>=inf,b<=sup)]
        img_show[:,:,1][np.logical_and(b>=inf,b<=sup)] = img_rgb[:,:,1][np.logical_and(b>=inf,b<=sup)]
        img_show[:,:,2][np.logical_and(b>=inf,b<=sup)] = img_rgb[:,:,2][np.logical_and(b>=inf,b<=sup)]
        
        return img_,img_show
    
    else:
        print("valor de Lab invalido")


"""_______________________________________________________________________________________"""


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