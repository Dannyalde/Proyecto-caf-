import numpy as np
import cv2 as cv

from .constans import *
from .utilts import (unfolding, folding)

class ColorSegmentation:

    def __init__(self,image):
        self.image = self._Segment_Coffe(image,lower = (0, -80, -10), upper = (85, 80, 80))

    def _companding_sRGB(self,rgb_values: np.ndarray):
        
        idx = rgb_values <= 0.04045
        rgb_values[idx] =  rgb_values[idx]/(12.92)
        rgb_values[~idx] = ((rgb_values[~idx]+0.055)/1.055)**2.4
        return rgb_values

    def _RGB2Lab(self,array_RGB: np.ndarray,fold: bool = True):

        if array_RGB.ndim == 3:
            rows, columns, bands = array_RGB.shape
            array_RGB = unfolding(array_RGB)
        array_RGB = self._companding_sRGB(array_RGB)
        xyz_linear = np.dot(array_RGB, RGB_LAB_MATRIX_D65.T)
        xyz_normalized = xyz_linear / XYZ_D65_STANDAR_ILUMINATION
        linear_condition = xyz_normalized > EPSILON
        XYZ = np.where(linear_condition, xyz_normalized ** (1 / 3), (xyz_normalized * 903.3 + 16) / 116)
        L = 116 * XYZ[:, 1] - 16
        L = np.clip(L, 0, 100)
        a = 500 * (XYZ[:, 0] - XYZ[:, 1])
        b = 200 * (XYZ[:, 1] - XYZ[:, 2])
        Lab = np.column_stack((L, a, b))
        if fold is True:
            Lab = folding(Lab, rows, columns, bands)
        return Lab
    
    def Lab2Lch(self, img_Lab: np.ndarray):

        rows, columns, bands = img_Lab.shape
        Lab = self._unfolding(img_Lab)
        L, a, b = Lab[:, 0], Lab[:, 1], Lab[:, 2]
        c = np.sqrt(a**2 + b**2)
        h = np.arctan2(b, a) * (180 / np.pi)
        h[h < 0] += 360
        Lch = folding(np.column_stack((L, c, h)), rows, columns, bands)
        return Lch
    
    def _Segment_Coffe(self, image, upper, lower):

        array_RGB = image.array
        mask_fg = image.background_mask
        Lab = np.zeros_like(image.array)
        Lab[mask_fg != 0] = self._RGB2Lab(array_RGB[mask_fg != 0], fold = False)
        mask = cv.inRange(Lab, upperb = upper, lowerb = lower)
        image_coffe = cv.bitwise_and(array_RGB, array_RGB, mask = mask)
        self.mask = cv.bitwise_and(mask_fg, mask_fg, mask = mask)
        return image_coffe

    def MaskLab_coffe(self, mask:tuple):

        mask_fg = self.mask.reshape(-1) != 0
        array_3D_RGB = self.image
        array_2D_RGB = unfolding(array_3D_RGB)

        mask_L, mask_a = mask 
        inf_L, sup_L = mask_L
        inf_a, sup_a = mask_a

        array_2D_Lab = self._RGB2Lab(array_3D_RGB,fold = False)
        array_2D_Lab_fg = array_2D_Lab[mask_fg]

        L,a = array_2D_Lab_fg[:,0], array_2D_Lab_fg[:,1]

        conditional  = np.logical_and
        mask_conditional = conditional(conditional(L >= inf_L, L <= sup_L), conditional(a >= inf_a,a <= sup_a))
        
        RGB_bad = np.ones_like(array_2D_RGB)
        RGB_good = np.ones_like(array_2D_RGB)

        Filler_RGB = array_2D_RGB[mask_fg]

        fill_data = RGB_bad[mask_fg]
        fill_data[~mask_conditional] = Filler_RGB[~mask_conditional]
        RGB_bad[mask_fg] = fill_data

        fill_data = RGB_good[mask_fg]
        fill_data[mask_conditional] = Filler_RGB[mask_conditional]
        RGB_good[mask_fg] = fill_data

        rows, columns, bands = array_3D_RGB.shape
        RGB_good = folding(RGB_good,rows, columns, bands)
        RGB_bad = folding(RGB_bad, rows, columns, bands)

        good_percent =(np.sum(mask_conditional)/np.sum(mask_fg))*100
        bad_percent = (np.sum(~mask_conditional)/np.sum(mask_fg))*100

        percent = (good_percent, bad_percent)

        class Results:
            pass

        results = Results()

        results.good_sample = RGB_good
        results.bad_sample = RGB_bad
        results.percent = percent

        return  results
    