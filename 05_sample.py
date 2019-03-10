# -*- coding: utf-8 -*-
###############################################################################
# Antes de ejecutar leer el archivo adjunto leer.txt
# Autor: Federico Cheda
# Contacto: federico.cheda@3edata.es
# Versión: 1.0
# Ejecucion en consola de ArcGis: 
# execfile('C:/script/python/arcgis/sample.py')
###############################################################################

# Imports
import sys
import os
import glob
import shutil
import subprocess
from subprocess import *
import Tkinter
from Tkinter import *
import tkFileDialog
###############################################################################
# Libreria de ArcGIS###########################################################
import arcpy #modulo de geoprocesos para ArcMAP
from arcpy import *
# Variables de entorno y desarrollo
arcpy.env.overwriteOutput = True # sobreescribir datos actuales
mxd = arcpy.mapping.MapDocument('CURRENT')
# #############################################################################

# Seleccionar directorios con Tkinter #########################################
# Directorio de almacenamiento de resultados
root = Tk()
root.withdraw()
dirProyecto = tkFileDialog.askdirectory(parent=root,
    initialdir='D:/3edata/OneDrive - 3edata Ingeniería Ambiental SL/3EDATA_GIS_TRABALLOS',
    title='Seleccionar la carpeta de salida del proyecto')
root.destroy()
# Directorio archivos a muestrear
root = Tk()
root.withdraw()
dirFotogramas = tkFileDialog.askdirectory(parent=root,
    initialdir='D:/3edata/OneDrive - 3edata Ingeniería Ambiental SL/3EDATA_GIS_TRABALLOS',
    title='Seleccionar directorio de archivos raster a muestrear')
root.destroy()
# Directorio archivos con delimitación del muestreo
root = Tk()
root.withdraw()
dirMuestreos = tkFileDialog.askdirectory(parent=root,
    initialdir='D:/3edata/OneDrive - 3edata Ingeniería Ambiental SL/3EDATA_GIS_TRABALLOS',
    title='Seleccionar directorio de archivos raster con la zona de muestreo')
root.destroy()

# crear arbol de directorios de salida #######################################0
dirBAT = os.path.join(dirProyecto,'00_bat/')
dirSample = ("D:/3edata/OneDrive - 3edata Ingeniería Ambiental SL/3EDATA_GIS_TRABALLOS/2018_3EDATA_GIS/20180000_ENCOROS/beche/2017_sample/")
# listas con datos de entrada para iterar #####################################
fotogramas = glob.glob(os.path.join(dirFotogramas,"*.tif"))
muestreos = glob.glob(os.path.join(dirMuestreos,"*.tif"))
###############################################################################

# Sample
# Replace a layer/table view name with a path to a dataset 
# (which can be a layer file) or create the layer/table view within the script
for fotograma in fotogramas:
    fName = os.path.basename(fotograma)
    for muestreo in muestreos:
        mName = os.path.basename(muestreo)
        arcpy.gp.Sample_sa(fotogrma, muestreo, fName+mName[-10:-4]+"_n.txt", "NEAREST", "Value", "CURRENT_SLICE")
        arcpy.gp.Sample_sa(fotogrma, muestreo, fName+mName[-10:-4]+"_b.txt", "BILINEAR ", "Value", "CURRENT_SLICE")
        arcpy.gp.Sample_sa(fotogrma, muestreo, fName+mName[-10:-4]+"_c.txt", "CUBIC", "Value", "CURRENT_SLICE")
        arcpy.gp.Sample_sa(fotogrma, muestreo, fName+mName[-10:-4]+"_m.txt", "MAJORITY", "Value", "CURRENT_SLICE")