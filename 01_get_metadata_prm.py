# -*- coding:utf-8 -*-
###############################################################################
# NORMALIZACIÓN Y CORRECIÓN RADIOMÉTRICA DE IMÁGENES MEDIANTE PANEL MICASENSE
# Válido para imágenese capturadas con el sensor MicaSense RedEdge 3 fware up 3
# Antes de ejecutar leer el archivo adjunto procedimiento.docx
# Punto: Corrección mediante Panel MicaSense
# Autor: Federico Cheda 
# Contacto: federico.cheda@3edata.es
# Version: 0.1
# Ejecución en python 3 o superior sobre consola de Anaconda con admin prvlg
# > activate micasense
# > python  C:/script/python/micasense/ip/geo/01_get_metadata_prm.py
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
import utm
import re

# Import tkinter
try:
    import tkinter as tk
    from tkinter import *
    from tkinter import filedialog
except ImportError:
    print('WARNING: tkinter no está presente en el sistema.')

# Check location of exiftool
exiftoolPath = None
if os.name == 'nt': #MS Windows
    print(os.name)
    exiftoolPath = 'C:/exiftool/exiftool.exe'
with exiftool.ExifTool(exiftoolPath) as exift:
    print('Exiftool run OK!')

# Seleccionar directorio de resultados
root = Tk()
root.withdraw()
outs_path = filedialog.askdirectory(parent=root,
    initialdir=r'D:/micasense/20181002_beche_micasense',
    title='Seleccionar el directorio de resultados')
root.destroy()

# Directorio de resultados
outs_dir = os.path.join(outs_path, 'imageprocessing_resultados/01_get_metadata')
if not os.path.exists(outs_dir):
    os.makedirs(outs_dir)

# Seleccionar directorio de imágenes
root = Tk()
root.withdraw()
image_path = filedialog.askdirectory(parent=root,
    initialdir=r'D:/micasense/20181002_beche_micasense',
    title='Seleccionar el directorio de imágenes a procesar')
root.destroy()

# Directorio para archivos BAT
dirBAT = os.path.join(outs_dir,'00_bat/')
if not os.path.exists(dirBAT):
    os.makedirs(dirBAT)

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

# Obtener coordenas GNSS de cada imagen a transformar
# Escribir metadatos de imagen en archivo .txt
gps_DecSecMinBat = os.path.join(dirBAT,"00_GNSS_DecSecMin.bat")
# exiftool code
# pathExiftool.exe -csv -r pathImages/*.tif -GPSLatitude -GPSLongitude -IrradianceYaw > pathOuts/GPS_DecSecMin.txt
try:
    with open(gps_DecSecMinBat,'w') as batWrite:
    # Escribir comando CMD
        batWrite.write("D:\ncd {0}\n{1} -csv -r IMG_*.tif -GPSLatitude -GPSLongitude -IrradianceYaw > {2}/00_GNSS_DecSecMin.txt".format(image_path, exiftoolPath, outs_dir))
    proc = subprocess.Popen(gps_DecSecMinBat,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = proc.communicate()
except:
    print("Error de ejecución del archivo: "+gps_DecSecMinBat)

gps_LatLongTxt = os.path.join(outs_dir, "01_GNSS_LatLong.txt")
try:
    with open(gps_LatLongTxt, 'w') as txtWrite:
        gps_DecSecMin = open(os.path.join(outs_dir,"00_GNSS_DecSecMin.txt"), "r")
        fila = 0
        linea = []
        for lineas in gps_DecSecMin.readlines():
            linea = re.findall(r"[\w.']+", lineas)
            if fila == 0:
                fila = fila + 1
                continue
            else:    
                img = str(linea[0])
                decN = float(linea[1])
                minN = float(linea[3][:-1])
                secN = float(linea[4])
                decW = float(linea[6])
                minW = float(linea[8][:-1])
                secW = float(linea[9])
                yaw = float(linea[11])
                if yaw > 0:
                    yaw = yaw
                else:
                    yaw = 360 + yaw
                lat = decN + (minN/60) + (secN/3600)
                lon = decW + (minW/60) + (secW/3600)
                txtWrite.write("{0},{1:3.10f},-{2:3.10f},{3:3.4f}\n".format(img, lat, lon, yaw))
    txtWrite.close()
    gps_DecSecMin.close()
    output, error = proc.communicate()
except:
    print("Error de escritura en el archivo: 01_GNSS_LatLong")

# Transformar coordenadas (Xpp,Ypp) WGS84 a (X, Y) UTM 29N

# Parametro de corrección de lente por banda para PuntoPrincipal
deltaX1 = float(-1.669)
deltaY1 = float(1.091)
deltaX2 = float(0.043)
deltaY2 = float(2.297)
deltaX3 = float(-1.909)
deltaY3 = float(1.609)
deltaX4 = float(-0.239)
deltaY4 = float(2.145)
gps_UTMTxt = os.path.join(outs_dir, "02_GNSS_UTM29T.txt")
try:
    with open(gps_UTMTxt, 'w') as utmWrite:
        gps_LatLong = open(gps_LatLongTxt, "r")
        linea = []
        for lineas in gps_LatLong.readlines():
            linea = lineas.split(',')
            print(linea)
            img = linea[0]
            lat = float(linea[1])
            lon = float(linea[2])
            yaw = float(linea[3])
            print(img)
            print(yaw)
            utmpp = utm.from_latlon(lat, lon)
            Xpp = float("{0:6.3f}".format(utmpp[0]))
            Ypp = float("{0:6.3f}".format(utmpp[1]))
            if linea[0][9] == '1':
                Xpp, Ypp = (Xpp+deltaX1), (Ypp+deltaY1)
                utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:3.4f}\n".format(img, Xpp, Ypp, yaw))
            elif linea[0][9] == '2':
                Xpp, Ypp = (Xpp+deltaX2), (Ypp+deltaY2)
                utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:3.4f}\n".format(img, Xpp, Ypp, yaw))
            elif linea[0][9] == '3':
                Xpp, Ypp = (Xpp+deltaX3), (Ypp+deltaY3)
                utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:3.4f}\n".format(img, Xpp, Ypp, yaw))
            elif linea[0][9] == '4':
                Xpp, Ypp = (Xpp+deltaX4), (Ypp+deltaY4)
                utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:3.4f}\n".format(img, Xpp, Ypp, yaw))
            elif linea[0][9] == '5':
                utmWrite.write("{0},{1:6.3f},{2:7.3f},{3:3.4f}\n".format(img, Xpp, Ypp, yaw))
    utmWrite.close()
    gps_LatLong.close()
    output, error = proc.communicate()
except:
    print("Error de escritura en el archivo: 02_GNSS_UTM29T ")