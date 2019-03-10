#! /usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Antes de ejecutar leer el archivo adjunto leer.txt
# Autor: Federico Cheda
# Contacto: federico.cheda@3edata.es
# Version: 0.0
# Ejecucion en python de Anaconda: python.exe path/alinear_img_mica_opencv2.py
# Ejecucion en consola de python: execfile('path/alinear_img_mica_opencv2.py')
# Instalación de Packages en C:/Anaconda3/pkgs
# Activate micasense en Anaconda consola
###############################################################################
import os
import sys
import subprocess
from subprocess import * 
import glob
import shutil
import numpy as np
import exiftool
import math
###
import cv2
from cv2 import *
import time
from time import sleep
#import libtiff
import PIL.Image as Image
###
import matplotlib.pyplot as plt
import multiprocessing
import micasense.capture as capture
import micasense.imageutils as imageutils
###
# import tkinter
try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog
except ImportError:
    print('WARNING: tkinter not present on your system.')
###############################################################################
# Seleccionar directorio de imágenes
root = Tk()
root.withdraw()
image_path = filedialog.askdirectory(parent=root,
    initialdir=r'C:/User/Usuario/Desktop/micasense/',
    title='Seleccionar el directorio de imágenes a procesar')
root.destroy()
# Seleccionar directorio de resultados
root = Tk()
root.withdraw()
outs_path = filedialog.askdirectory(parent=root,
    initialdir=r'C:/Users/Usuario/Desktop/micasense/',
    title='Seleccionar el directorio de resultados')
root.destroy()
# Directorio de resultados
dir_outs = os.path.join(outs_path, 'imageprocessing_resultados/02_set_align/')
if os.path.exists(dir_outs):
    shutil.rmtree(dir_outs)
if not os.path.exists(dir_outs):
    os.makedirs(dir_outs)


b1, b2, b3, b4, b5 = 0, 1, 2, 3, 4
image_names = glob.glob(os.path.join(image_path,'IMG_*.tif'))
fotogramas = len(image_names)
fotrogramasG = int(fotogramas/5)
j = 0
try:
    for it in range(fotrogramasG):
        print(image_names[b1])
        print(image_names[b2])
        print(image_names[b3])
        print(image_names[b4])
        print(image_names[b5])
        #'''
        im1 =  cv2.imread(image_names[b1],-1);
        im2 =  cv2.imread(image_names[b2],-1);
        im3 =  cv2.imread(image_names[b3],-1);
        im4 =  cv2.imread(image_names[b4],-1);
        im5 =  cv2.imread(image_names[b5],-1);
        
        # Find size of image1
        sz = im1.shape
        scaling_factor = (4294967296/65536)
        res1 = np.float32(im1)
        res1 = res1*scaling_factor
        res2 = np.float32(im2)
        res2 = res2*scaling_factor
        res3 = np.float32(im3)
        res3 = res3*scaling_factor
        res4 = np.float32(im4)
        res4 = res4*scaling_factor
        res5 = np.float32(im5)
        res5 = res5*scaling_factor

        resLista = [res1, res2, res3, res4]

        i=1
        imagen = im1
        try:
            for resX in resLista:
                print('Alineando banda:'+str(i))
                # Define the motion model
                warp_mode = cv2.MOTION_TRANSLATION  
                 
                # Define 2x3 or 3x3 matrices and initialize the matrix to identity
                if warp_mode == cv2.MOTION_HOMOGRAPHY :
                    warp_matrix = np.eye(3, 3, dtype=np.float32)
                else :
                    warp_matrix = np.eye(2, 3, dtype=np.float32)
                 
                # Specify the number of iterations.
                number_of_iterations = 100;
                 
                # Specify the threshold of the increment
                # in the correlation coefficient between two iterations
                termination_eps = 1e-10;
                 
                # Define termination criteria
                criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)
                 
                # Run the ECC algorithm. The results are stored in warp_matrix.
                try:
                    (cc, warp_matrix) = cv2.findTransformECC (res5, resX, warp_matrix, warp_mode, criteria)
                except:
                    # PASS: sólo influye a efectos de corrección de frame.
                    # No se oculta ningun error determinante en el algoritmo. Por eso se permite el Except: pass
                    pass            
                if warp_mode == cv2.MOTION_HOMOGRAPHY :
                    # Use warpPerspective for Homography 
                    im_aligned = cv2.warpPerspective (imagen, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
                else :
                    # Use warpAffine for Translation, Euclidean and Affine
                    im_aligned = cv2.warpAffine(imagen, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);

                # Show final results
                #time.sleep(0.1)
                imgA = cv2.imshow("Aligned Image Banda "+str(i), im_aligned)
                cv2.imwrite(os.path.join(dir_outs, os.path.basename(image_names[j])), im_aligned);
                cv2.waitKey(100)
                if i == 1:
                    imagen = im2
                if i == 2:
                    imagen = im3
                if i == 3:
                    imagen = im4
                if i == 4:
                    i = 1
                    imagen = im1
                i += 1
                j += 1
        except:
            print('Error de ejecución: ')
        cv2.imwrite(os.path.join(dir_outs,os.path.basename(image_names[j])),im5);
        b1, b2, b3, b4, b5 = b1+5, b2+5, b3+5, b4+5, b5+5
        j += 1
except:
    print('Error de ejecución: ')