# -*- coding:utf-8 -*-
###############################################################################
# NORMALIZACIÓN Y CORRECIÓN RADIOMÉTRICA DE IMÁGENES MEDIANTE PANEL MICASENSE
# Válido para imágenese capturadas con el sensor MicaSense
# Antes de ejecutar leer el archivo adjunto procedimiento.docx
# Punto: Corrección mediante Panel MicaSense
# Autor: Federico Cheda 
# Contacto: federico.cheda@3edata.es
# Version: 0.1
# Ejecución en consola de python 3 o superior: consola de Anaconda admin prvlg
# > activate micasense
# > python  C:/script/python/micasense/ok/1_nd_rad_ref.py
###############################################################################

import cv2
import exiftool
import numpy as numpy
import matplotlib.pyplot as plt
import os
import glob
import math
#import subprocess
import tkinter
from tkinter import *
from tkinter import filedialog
#%matplotlib inline  # no funcionan las magic lines --- intentar solucionar
#from libtiff import TIFFimage
from PIL import Image

import shutil
import subprocess
from subprocess import *
# librería micasense
import micasense.image as image
import micasense.plotutils as plotutils
import micasense.utils as msutils
import micasense.metadata as metadata
import micasense.capture as capture
import micasense.panel as panel

# path para imágenes
#imagePath = os.path.join('.','data','0000SET','000')
#imagePath = r'C:/script/micasense/imageprocessing/data/0000SET/000/'

# asignar directorios con Tkinter #############################################
# path para imágenes RAW
root = Tk()
root.withdraw()
imagePath = filedialog.askdirectory(parent=root,
    initialdir=r'C:/Users/Usuario/Desktop/micasense/imageprocessing_resultados',
    title='Seleccionar el directorio de imágenes a procesar')
root.destroy()
# Seleccionar directorio de resultados
root = Tk()
root.withdraw()
outsPath = filedialog.askdirectory(parent=root,
    initialdir=r'C:/Users/Usuario/Desktop/micasense',
    title='Seleccionar el directorio de resultados')
root.destroy()
# path para imágenes procesadas a reflectancia
dirOuts = os.path.join(outsPath,'imageprocessing_resultados/03_set_reflectance')
if not os.path.exists(dirOuts):
    os.makedirs(dirOuts)
# directorio para archivos BAT
'''
dirBAT = os.path.join(dirOuts,'00_bat/')
if not os.path.exists(dirBAT):
    os.makedirs(dirBAT)
'''
# check exiftool
exiftoolPath = None
if os.name == 'nt': #OS MS Windows
    print(os.name)
    exiftoolPath = 'C:/exiftool/exiftool.exe'
with exiftool.ExifTool(exiftoolPath) as exift:
    print('Exiftool run OK!')
###############################################################################
# asignar blanco para la banda NIR
root = Tk()
root.withdraw()
#targetName = os.path.join(imagePath, 'IMG_0000_1.tif')
targetName = filedialog.askopenfilename(parent=root,
    initialdir=imagePath,
    title='Seleccionar el blanco: banda NIR')
root.destroy()
print(targetName)

######################################################################TUTORIAL1
print("Conversión de ND RAW a RADIANCIA a REFLECTANCIA")
#'''
# matriz de datos de imagen -> objeto variable 
imageRaw = plt.imread(targetName)
# plot al target
plotutils.colormap('gray')
plot = plotutils.plotwithcolorbar(imageRaw, title='Raw target ND')

# obtener metadatos de la imagen
meta = metadata.Metadata(targetName, exiftoolPath=exiftoolPath)
firmwareVersion = meta.get_item('EXIF:Software')
bandName = meta.get_item('XMP:BandName')

# convertir ND RAW a Radiancia
radianceImage, L, V, R = msutils.raw_image_to_radiance(meta, imageRaw)
# plotutils.plotwithcolorbar(V,'Vignette Factor');
# plotutils.plotwithcolorbar(R,'Row Gradient Factor');
# plotutils.plotwithcolorbar(V*R,'Combined Corrections');
# plotutils.plotwithcolorbar(L,'Vignette and row gradient corrected raw values');
# plotutils.plotwithcolorbar(radianceImage,'All factors applied and scaled to radiance');

# Estas coordenadas se deben modificar para cada procesado según blanco
# Dato debe ser introducido manualmente (coordenadas del blanco)
targetImage = radianceImage.copy()
print('Set upper left column (x coordinate) of panel area')
ulx = eval(input()) # upper left column (x coordinate) of panel area
while ulx < 99 or ulx > 1101:
    print('Invalid input value.\nSet upper left column (x coordinate) of panel area')
    ulx = eval(input()) # upper left column (x coordinate) of panel area
print('Set upper left row (y coordinate) of panel area')
uly = eval(input()) # upper left row (y coordinate) of panel area
while uly < 99 or uly > 801:
    print('Invalid input value.\nSet upper left row (y coordinate) of panel area')
    uly = eval(input()) # upper left column (x coordinate) of panel area
print('Set lower right column (x coordinate) of panel area')
lrx = eval(input()) # lower right column (x coordinate) of panel area
while lrx < 199 or lrx > 1201:
    print('Invalid input value.\nSet lower right column (x coordinate) of panel area')
    lrx = eval(input()) # upper left column (x coordinate) of panel area
print('Set lower right row (y coordinate) of panel area')
lry = eval(input()) # lower right row (y coordinate) of panel area
while lry < 199 or lry > 901:
    print('Invalid input value.\nSet lower right row (y coordinate) of panel area')
    lry = eval(input()) # upper left column (x coordinate) of panel area
cv2.rectangle(targetImage,(ulx,uly),(lrx,lry),(0,255,0),3)

# parámetros de calibración del blanco
panelCalibration = { 
    "Blue": 0.72, 
    "Green": 0.74, 
    "Red": 0.73,
    "Red edge": 0.72, 
    "NIR": 0.67
}

# Select panel region from radiance image
panelRegion = radianceImage[uly:lry, ulx:lrx]
#plotutils.plotwithcolorbar(targetImage, title='Panel en niveles de radiancia');
meanRadiance = panelRegion.mean()
panelReflectance = panelCalibration[bandName]
radianceToReflectance = panelReflectance/meanRadiance
#radianceToReflectance = panelReflectance/0.67
print('Radiance to reflectance conversion factor: {:1.3f}'.format(radianceToReflectance))

reflectanceImage = radianceImage*radianceToReflectance
#plotutils.plotwithcolorbar(reflectanceImage, 'Converted Reflectane Image');

panelRegionRaw = imageRaw[uly:lry, ulx:lrx]
panelRegionRefl = reflectanceImage[uly:lry, ulx:lrx]
panelRegionReflBlur = cv2.GaussianBlur(panelRegionRefl,(5,5),5)
#plotutils.plotwithcolorbar(panelRegionReflBlur, 'Smoothed panel region in reflectance image')
print('Min Reflectance in panel region: {:1.2f}'.format(panelRegionRefl.min()))
print('Max Reflectance in panel region: {:1.2f}'.format(panelRegionRefl.max()))
print('Mean Reflectance in panel region: {:1.2f}'.format(panelRegionRefl.mean()))
print('Standard deviation in region: {:1.4f}'.format(panelRegionRefl.std()))

# correct for lens distortions to make straight lines straight
undistortedReflectance = msutils.correct_lens_distortion(meta, reflectanceImage)
#plotutils.plotwithcolorbar(undistortedReflectance, 'Undistorted reflectance image')
print('PerspectiveFocalLength: '+(str(meta.get_item('XMP:PerspectiveFocalLength'))))
#

#Procesado banda NIR (1)
imgs = glob.glob(os.path.join(imagePath, "*4.tif"))
for img in imgs:
    #flightImageName = os.path.join(imagePath,'IMG_0003_1.tif')
    #flightImageName = img

    flightImageRaw=plt.imread(img)
    #plotutils.plotwithcolorbar(flightImageRaw, 'Raw ND Image');

    flightRadianceImage, _, _, _ = msutils.raw_image_to_radiance(meta, flightImageRaw)
    flightReflectanceImage = flightRadianceImage * radianceToReflectance
    #plotutils.plotwithcolorbar(flightReflectanceImage, 'Raw ND to Reflectance');
    # no funciona correct_lens_distortion(,)
    flightUndistortedReflectance = msutils.correct_lens_distortion(meta, flightReflectanceImage)
    #plotutils.plotwithcolorbar(flightUndistortedReflectance, 'Reflectance converted and undistorted image');

    im = Image.fromarray(flightUndistortedReflectance)
    im.save(os.path.join(dirOuts, os.path.basename(img)))

'''
# Copiar metadatos de las imágense originaes a las procesadas
metadataBat = os.path.join(dirBAT,"04_metadata_NIR.bat")

try:
    with open(metadataBat,'w') as batWrite:
    # escribir comando CMD
        for img in imgs:
            iname = os.path.basename(img)
            batWrite.write("C:/exiftool/exiftool.exe -TagsFromFile {0} -all:all>all:all {1}\n".format(os.path.join(imagePath, iname), os.path.join(dirOuts, iname)))
    proc = subprocess.Popen(metadataBat,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = proc.communicate()
except:
    print("Error de ejecución: "+metadataBat)


    #break
#'''