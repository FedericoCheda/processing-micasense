# -*- coding:utf-8 -*-
###############################################################################
# Descripción
# Válido para imágenese capturadas con el sensor MicaSense
# Antes de ejecutar leer el archivo adjunto procedimiento.docx
# Punto: 
# Autor: Federico Cheda 
# Contacto: federico.cheda@3edata.es
# Version: 0.1
# Ejecución en python 3 o superior sobre consola de Anaconda con admin prvlg
# > activate micasense
# > python  C:/script/python/micasense/ip/04_set_coordinates_ms_3d.py

### Imports ###################################################################
import os
import sys
import subprocess
from subprocess import * 
import glob
import shutil
import numpy as np
import exiftool
import math
# Import tkinter
try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog
except ImportError:
    print('WARNING: tkinter no está presente en su sistema.')
# Check location of exiftool
exiftoolPath = None
if os.name == 'nt': #MS Windows
    print(os.name)
    exiftoolPath = 'C:/exiftool/exiftool.exe'
with exiftool.ExifTool(exiftoolPath) as exift:
    print('Exiftool run OK!')

### Parámetros fijos ##########################################################
# coordenadas fijas en sistema fotográfico 1 (pixeles)
xpp = 0 # Nunca está en el (0, 0)
ypp = 0 # Nunca está en el (0, 0)
c = -1463.4
x1 = -640
y1 = 480
x2 = 640
y2 = 480
x3 = 640
y3 = -480
x4 = -640
y4 = -480
# distancias en pixeles(_p) de los ejes del fotograma
x_p = 1280 #pixeles en sentido del eje x
y_p = 960 #pixeles en sentido del eje y
# milímetros(_mm) y metros(_m)
c_mm = 5.45
c_m = 0.00545 # aproximados para cada banda
x_mm = 4.79999999999999982236
y_mm = 3.60000000000000008882
d_mm = 2.99999999999999995559
d_p_mm = 6.22
# cota del agua
cota_agua = 121.5
# Variación espacial del centro óptico con respecto a banda 5 para 120m
deltaX1 = float(-1.669)
deltaY1 = float(1.091)
deltaX2 = float(0.043)
deltaY2 = float(2.297)
deltaX3 = float(-1.909)
deltaY3 = float(1.609)
deltaX4 = float(-0.239)
deltaY4 = float(2.145)
### Parámetros variables ######################################################
# giros de la matriz de rotación de Euler
g_omega = float(0)
g_phi = float(0)
g_kappa = float(0)

# Seleccionar directorio de proyecto
root = Tk()
root.withdraw()
dir_path = filedialog.askdirectory(parent=root,
    initialdir=r'D:',
    title='Seleccionar el directorio de resultados')
root.destroy()
# Directorio de entrada de metadatos
root = Tk()
root.withdraw()
dir_met = filedialog.askdirectory(parent=root,
    initialdir=r'D:',
    title='Seleccionar el directorio de metadatos external_camera_parameters.txt')
root.destroy()
# Directorio de resultados de procesado
dir_outs = os.path.join(dir_path,'imageprocessing_resultados/04_set_coordinates_pix4d/')
if not os.path.exists(dir_outs):
    os.makedirs(dir_outs)
# Directorio de resultados de imágenes geo
dir_outs_tif = os.path.join(dir_path,'imageprocessing_resultados/05_set_geotif/')
if not os.path.exists(dir_outs_tif):
    os.makedirs(dir_outs_tif)
# Seleccionar directorio de imágenes
root = Tk()
root.withdraw()
image_path = filedialog.askdirectory(parent=root,
    initialdir=os.path.join(dir_path,'imageprocessing_resultados/03_set_reflectance/'),
    title='Seleccionar el directorio de imágenes a procesar')
root.destroy()

# Directorio de archivos de coordenadas para georreferenciar imágenes
dirXY_V4 = os.path.join(dir_outs,'coordenadas')
if not os.path.exists(dirXY_V4):
    os.makedirs(dirXY_V4)

# Obtener coordenas GNSS de cada vértice de cada imagen
gps_UTMTxt = os.path.join(dir_met, "external_camera_parameters.txt")
gps_UTMTxt_V4 = os.path.join(dir_outs, "03_GNSS_UTM29T_V4.txt")
gps_UTM = open(gps_UTMTxt, 'r')
linea = []
cabecera = True
try:
    with open(gps_UTMTxt_V4, 'w') as utmWrite:
        for lineas in gps_UTM.readlines():
            print(lineas)
            linea = lineas.split(';')
            if cabecera == False:
                img = linea[0]
                Xo = float(linea[1]) 
                Yo = float(linea[2])
                Zo = float(linea[3])
                #'''
                if linea [0][9] == '1':
                    Xo = float(linea[1]) #+ deltaX1
                    Yo = float(linea[2]) #+ deltaY1
                    Zo = float(linea[3])
                    c = -1454.82 
                if linea [0][9] == '2':
                    Xo = float(linea[1]) #+ deltaX2
                    Yo = float(linea[2]) #+ deltaY2
                    Zo = float(linea[3])
                    c = -1453.86
                if linea [0][9] == '3':
                    Xo = float(linea[1]) #+ deltaX3
                    Yo = float(linea[2]) #+ deltaY3
                    Zo = float(linea[3])
                    c = -1462.32
                if linea [0][9] == '4':
                    Xo = float(linea[1]) #+ deltaX4
                    Yo = float(linea[2]) #+ deltaY4
                    Zo = float(linea[3])
                    c = -1456.30
                if linea [0][9] == '5':
                    Xo = float(linea[1]) 
                    Yo = float(linea[2])
                    Zo = float(linea[3])
                    c = -1458.56 
                #'''
                g_omega = float(linea[4])
                g_phi = float(linea[5])
                g_kappa = float(linea[6])
                print(linea)
                
                # Helmert 2d transformación afín proyectiva (giro, traslación, escala)
                # X = Tx + lambda * (x' cos(rad) - y' sin(rad))
                # Y = Ty + lambda * (x' sin(rad) + y' cos(rad))

                # lambda = factor de escala (relación pixel con distancia en terreno)
                h_vuelo = Zo - cota_agua # altura de vuelo
                lambdaE = h_vuelo*(0.082/115) # Factor de escala según altura de vuelo
                #print('lambdaE: ',lambdaE) # print de control, comentar
                # Helmert 3d (lambda, omega, phi, kappa, Tx, Ty, Tz)
                # Condición de colinealidad
                # Giros del sistema de coordenadas
                omega = math.radians(g_omega)
                phi = math.radians(g_phi)
                kappa = math.radians(g_kappa)
                # Parámetros de la matriz de Euler [3x3]. 
                a11 = math.cos(phi)*math.cos(kappa)
                a12 = - math.cos(phi)*math.sin(kappa)
                a13 = math.sin(phi)
                a21 = math.cos(omega)*math.sin(kappa) + math.sin(omega)*math.sin(phi)*math.cos(kappa)
                a22 = math.cos(omega)*math.cos(kappa) - math.sin(omega)*math.sin(phi)*math.sin(kappa)
                a23 = - math.sin(omega)*math.cos(phi)
                a31 = math.sin(omega)*math.sin(kappa) - math.cos(omega)*math.sin(phi)*math.cos(kappa)
                a32 = math.sin(omega)*math.cos(kappa) + math.cos(omega)*math.sin(phi)*math.sin(kappa)
                a33 = math.cos(omega)*math.cos(phi)
                # Coordenadas terreno del centro de proyección y los cuatro vértices
                # Se debe tener en cuenta que los vertices en tierra cuentan con desplazamiento por relieve
                Xpp = (lambdaE * ((a11*xpp)+(a12*ypp)+(a13*c))) + Xo
                Ypp = (lambdaE * ((a21*xpp)+(a22*ypp)+(a23*c))) + Yo
                Zpp = (lambdaE * ((a31*xpp)+(a32*ypp)+(a33*c))) + Zo
                X1 = (lambdaE * ((a11*x1)+(a12*y1)+(a13*c))) + Xo
                Y1 = (lambdaE * ((a21*x1)+(a22*y1)+(a23*c))) + Yo
                Z1 = (lambdaE * ((a31*x1)+(a32*y1)+(a33*c))) + Zo
                X2 = (lambdaE * ((a11*x2)+(a12*y2)+(a13*c))) + Xo
                Y2 = (lambdaE * ((a21*x2)+(a22*y2)+(a23*c))) + Yo
                Z2 = (lambdaE * ((a31*x2)+(a32*y2)+(a33*c))) + Zo
                X3 = (lambdaE * ((a11*x3)+(a12*y3)+(a13*c))) + Xo
                Y3 = (lambdaE * ((a21*x3)+(a22*y3)+(a23*c))) + Yo
                Z3 = (lambdaE * ((a31*x3)+(a32*y3)+(a33*c))) + Zo
                X4 = (lambdaE * ((a11*x4)+(a12*y4)+(a13*c))) + Xo
                Y4 = (lambdaE * ((a21*x4)+(a22*y4)+(a23*c))) + Yo
                Z4 = (lambdaE * ((a31*x4)+(a32*y4)+(a33*c))) + Zo
                print('Control de coordenadas para la imagen: ',img)
                utmWrite.write('{0},{1:6.3f},{2:7.3f},{3:6.3f},{4:7.3f},{5:6.3f},{6:7.3f},{7:6.3f},{8:7.3f},{9:3.4f}\n'.format(img, X1, Y1, X2, Y2, X3, Y3, X4, Y4, g_kappa))
            else:
                cabecera = False
                continue    
        utmWrite.close()
        gps_UTM.close()
    output, error = proc.communicate()
except:
    print("Error de escritura en el archivo: 03_GNSS_UTM29T_V4.txt ")

### Crear archivo de georreferenciación para cada imagen ######################
# resultado compatible con la georeferenciación en ArcGIS

# coordenadas fijas de los vértices de cada imagen (sistema imágen)
x1 = 0 # coordenada X superior izquierda
y1 = 0 # coordenada Y superior izquierda
x2 = 1280 # coordenada X superior derecha
y2 = 0 # coordenada Y superior derecha
x3 = 1280 # coordenada X inferior derecha
y3 = -960 # coordenada Y inferior derecha
x4 = 0 # coordenada X inferior izquierda
y4 = -960 # coordenada Y inferior izquierda

# leer ('r') archivo de coordenadas de vertices
gpsUTM = open(gps_UTMTxt_V4, 'r')
linea = [] # lista vacia

# iterar archivo de cordenadas línea a línea
for lineas in gpsUTM.readlines():
    linea = lineas.split(',')
    img = linea[0] # identificador único de cada imagen(IMG_xxxx_y.tif) xxxx = numeración, y = banda
    # coordenadas variables de los vértices de cada imagen (sistema terreno)    
    X1 = float(linea[1]) # coordenada X superior izquierda
    Y1 = float(linea[2]) # coordenada Y superior izquierda
    X2 = float(linea[3]) # coordenada X superior derecha
    Y2 = float(linea[4]) # coordenada Y superior derecha
    X3 = float(linea[5]) # coordenada X inferior derecha
    Y3 = float(linea[6]) # coordenada Y inferior derecha
    X4 = float(linea[7]) # coordenada X inferior izquierda
    Y4 = float(linea[8]) # coordenada Y inferior izquierda
    # crear archivo de coordenadas individual para cada imagen
    coordTxt = os.path.join(dirXY_V4,img[:-3]+'txt')
    # escribir coordenadas en archivo individual para cada imagen
    try:
        with open(coordTxt, 'w') as coordWrite:
            coordWrite.write("{0},{1},{2:6.3f},{3:7.3f}\n{4},{5},{6:6.3f},{7:7.3f}\n{8},{9},{10:6.3f},{11:7.3f}\n{12},{13},{14:6.3f},{15:7.3f}".format(x1, y1, X1, Y1, x2, y2, X2, Y2, x3, y3, X3, Y3, x4, y4, X4, Y4))
            coordWrite.close()
        output, error = proc.communicate()
    except:
        print("Error de escritura en el archivo:" )
# cerrar archivo de coordenadas de vertices      
gpsUTM.close()
