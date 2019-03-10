# -*- coding:utf-8 -*-
###############################################################################
# NORMALIZACIÓN Y CORRECIÓN RADIOMÉTRICA DE IMÁGENES MEDIANTE PANEL MICASENSE
# Válido para imágenese capturadas con el sensor MicaSense
# Antes de ejecutar leer el archivo adjunto procedimiento.docx
# Punto: Corrección mediante Panel MicaSense
# Autor: Federico Cheda 
# Contacto: federico.cheda@3edata.es
# Version: 0.1
# Ejecución en python 3 o superior sobre consola de Anaconda con admin prvlg
# > activate micasense
# > python  C:/script/python/micasense/ip/geo/04_set_coordinates_ms.py
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

# Seleccionar directorio de proyecto
root = Tk()
root.withdraw()
dir_path = filedialog.askdirectory(parent=root,
    initialdir=r'C:/Users/Usuario/Desktop/micasense/',
    title='Seleccionar el directorio de resultados')
root.destroy()

# Directorio de entrada de metadatos
dir_met = os.path.join(dir_path,'imageprocessing_resultados/01_get_metadata/')
if not os.path.exists(dir_met):
    os.makedirs(dir_met)
# Directorio de resultados de procesado
dir_outs = os.path.join(dir_path,'imageprocessing_resultados/04_set_coordinates/')
if not os.path.exists(dir_outs):
    os.makedirs(dir_outs)

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

# Coordenadas fijas en sistema fotográfico
xpp = 640
ypp = -480
x1 = 0
y1 = 0
x2 = 1280
y2 = 0
x3 = 1280
y3 = -960
x4 = 0
y4 = -960

# Obtener coordenas GNSS de cada vertice de cada imagen
gps_UTMTxt = os.path.join(dir_met, "02_GNSS_UTM29T.txt")
gps_UTMTxt_V4 = os.path.join(dir_outs, "03_GNSS_UTM29T_V4.txt")
gps_UTM = open(gps_UTMTxt, "r")
linea = []
try:
    with open(gps_UTMTxt_V4, 'w') as utmWrite:
        gps_UTM = open(gps_UTMTxt, "r")
        for lineas in gps_UTM.readlines():
            linea = lineas.split(',')
            img = linea[0]
            Xpp = float(linea[1])
            Ypp = float(linea[2])
            yaw = float(linea[3])
            print(img)
            #print(yaw)

            # Helmert 2d transformación afín proyectiva (giro, traslación, escala)
            # X = Tx + lambda * (x' cos(rad) - y' sin(rad))
            # Y = Ty + lambda * (x' sin(rad) + y' cos(rad))

            # Tx, Ty = traslación en x e y
            # lambda = factor de escala (relación pixel con distancia en terreno)
            lambdaE = 0.082 # factor de escala para vuelos a 120m de altura
            # alpha = ángulo de rotación del sistema, conversión de geográfico (N) a polar (X) 
            alpha = (450 - yaw)
            # Distancia del centro a vertices del fotogrma en terreno (situación teórica ideal)
            d = ((math.sqrt(math.pow(x3/2, 2)+math.pow(y3/2, 2))) * lambdaE)
            # relación de ángulos pp fotograma / vertices
            delta = float(math.degrees(math.atan(x3/-y3)))
            # Tx = X - lambda * (x' cos(rad) - y' sin(rad))
            # Ty = Y - lambda * (x' sin(rad) + y' cos(rad))
            Tx = float("{0:6.3f}".format(Xpp + d*math.cos(math.radians(alpha+delta))))
            Ty = float("{0:7.3f}".format(Ypp + d*math.sin(math.radians(alpha+delta))))
            #print('Tx = ', '%.3f' % Tx)
            #print('Ty = ', '%.3f' % Ty)
            X1 = Tx
            Y1 = Ty
            #print('X1 = ', '%.3f' % X1)
            #print('Y1 = ', '%.3f' % Y1)
            X2 = float("{0:6.3f}".format(Xpp + d*math.cos(math.radians(alpha-delta))))
            Y2 = float("{0:7.3f}".format(Ypp + d*math.sin(math.radians(alpha-delta))))
            #print('X2 = ', '%.3f' % X2)
            #print('Y2 = ', '%.3f' % Y2)
            X3 = float("{0:6.3f}".format(Xpp + d*math.cos(math.radians(alpha+delta-180))))
            Y3 = float("{0:7.3f}".format(Ypp + d*math.sin(math.radians(alpha+delta-180))))
            #print('X3 = ', '%.3f' % X3)
            #print('Y3 = ', '%.3f' % Y3)
            X4 = float("{0:6.3f}".format(Xpp + d*math.cos(math.radians(alpha-delta+180))))
            Y4 = float("{0:7.3f}".format(Ypp + d*math.sin(math.radians(alpha-delta+180))))
            #print('X4 = ', '%.3f' % X4)
            #print('Y4 = ', '%.3f' % Y4)
            # Comprobar distancias entre pares de puntos terreno para verificar funcionamiento
            d12 = math.sqrt(pow((X2-X1),2)+pow((Y2-Y1),2))
            d23 = math.sqrt(pow((X3-X2),2)+pow((Y3-Y2),2))
            d34 = math.sqrt(pow((X4-X3),2)+pow((Y4-Y3),2))
            d41 = math.sqrt(pow((X1-X4),2)+pow((Y1-Y4),2))
            print('d12 = ', '%.3f' % d12)
            print('d23 = ', '%.3f' % d23)
            print('d34 = ', '%.3f' % d34)
            print('d41 = ', '%.3f' % d41)
            utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:6.3f},{4:7.3f},{5:6.3f},{6:7.3f},{7:6.3f},{8:7.3f},{9:3.4f}\n".format(img, X1, Y1, X2, Y2, X3, Y3, X4, Y4, yaw))
        utmWrite.close()
        gps_UTM.close()
    output, error = proc.communicate()
except:
    print("Error de escritura en el archivo: 03_GNSS_UTM29T_V4.txt ")

gpsUTM = open(gps_UTMTxt_V4, 'r')
linea = []
for lineas in gpsUTM.readlines():
    #print(linea)
    linea = lineas.split(',')
    img= linea[0]
    X1= float(linea[1])
    Y1= float(linea[2])
    X2= float(linea[3])
    Y2= float(linea[4])
    X3= float(linea[5])
    Y3= float(linea[6])
    X4= float(linea[7])
    Y4= float(linea[8])

    coordTxt = os.path.join(dirXY_V4,img[:-3]+'txt')
    #print(coordTxt)
    try:
        with open(coordTxt, 'w') as coordWrite:
            coordWrite.write("{0},{1},{2:6.3f},{3:7.3f}\n{4},{5},{6:6.3f},{7:7.3f}\n{8},{9},{10:6.3f},{11:7.3f}\n{12},{13},{14:6.3f},{15:7.3f}".format(x1, y1, X1, Y1, x2, y2, X2, Y2, x3, y3, X3, Y3, x4, y4, X4, Y4))
        coordWrite.close()
        output, error = proc.communicate()
    except:
        print("Error de escritura en el archivo: img_coordenadas.txt ")
    #break
gpsUTM.close()
#'''