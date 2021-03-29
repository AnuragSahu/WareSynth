import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from shutil import copyfile
import Constants
import random

dataDirs = [name for name in os.listdir(".") if os.path.isdir(name) and "datasets" in name]
dataDirs.sort()

# Create output directories
outputDir = "datasets"
labelSubDir = "/anuragAnnotations/labels"
warehouseSubDir = "/anuragAnnotations/warehouse"
if(Constants.GENERATE_KITTI):
    KITTILabelSubDir = "/KITTI/label_2"
    KITTIImageSubDir = "/KITTI/image_2"
    KITTIDepthSubDir = "/KITTI/depth"
    KITTIVelodyneSubDir = "/KITTI/velodyne"
    KITTIcalibSubDir = "/KITTI/calib"
    KITTILabelOutputDir = outputDir + KITTILabelSubDir
    KITTIImageOutputDir = outputDir + KITTIImageSubDir
    KITTIDepthOutputDir = outputDir + KITTIDepthSubDir
    KITTIVelodyneOutputDir = outputDir + KITTIVelodyneSubDir
    KITTIcalibOutputDir = outputDir + KITTIcalibSubDir
    Path(KITTILabelOutputDir).mkdir(parents=True, exist_ok=True)
    Path(KITTIImageOutputDir).mkdir(parents=True, exist_ok=True)
    Path(KITTIDepthOutputDir).mkdir(parents=True, exist_ok=True)
    Path(KITTIVelodyneOutputDir).mkdir(parents=True, exist_ok=True)
    Path(KITTIcalibOutputDir).mkdir(parents=True, exist_ok=True)
    KITTIVelodyneIndx = 0
    KITTIDepthIndx = 0
    KITTIcalibIndx = 0
    KITTIImageIndx = 0
    KITTILabelIndx = 0

outputLabelDir = outputDir + labelSubDir
outputWarehouseDir = outputDir + warehouseSubDir

Path(outputLabelDir).mkdir(parents=True, exist_ok=True)
Path(outputWarehouseDir).mkdir(parents=True, exist_ok=True)

labelIdx = 0
imageIdx = 0

def copyFilesInDir(indx, destinationDirectory, sourceDirectory, fileNames):
    for fileName in fileNames:
        extension = fileName.split(".")[-1]
        copyfile(os.path.join(sourceDirectory, fileName), os.path.join(destinationDirectory, str(indx).zfill(6)+"."+extension))
        indx += 1
    return indx

for directory in dataDirs:
    
    labelDir = directory + labelSubDir
    warehouseDir = directory + warehouseSubDir
    if(Constants.GENERATE_KITTI):
        KITTILabelDir = directory + KITTILabelSubDir
        KITTIImageDir = directory + KITTIImageSubDir
        KITTIDepthDir = directory + KITTIDepthSubDir
        KITTIVelodyneDir = directory + KITTIVelodyneSubDir
        KITTIcalibDir = directory + KITTIcalibSubDir
        KITTILabels = [f for f in listdir(KITTILabelDir) if isfile(join(KITTILabelDir, f))]
        KITTILabels.sort()
        KITTIImages = [f for f in listdir(KITTIImageDir) if isfile(join(KITTIImageDir, f))]
        KITTIImages.sort()
        KITTIDepths = [f for f in listdir(KITTIDepthDir) if isfile(join(KITTIDepthDir, f))]
        KITTIDepths.sort()
        KITTIvelodyne = [f for f in listdir(KITTIVelodyneDir) if isfile(join(KITTIVelodyneDir, f))]
        KITTIvelodyne.sort()
        KITTICalibs = [f for f in listdir(KITTIcalibDir) if isfile(join(KITTIcalibDir, f))]
        KITTICalibs.sort()
    
    labels = [f for f in listdir(labelDir) if isfile(join(labelDir, f))]
    labels.sort()
    images = [f for f in listdir(warehouseDir) if isfile(join(warehouseDir, f))]
    images.sort()

    labelIdx = copyFilesInDir(labelIdx, outputLabelDir, labelDir, labels)
    imageIdx = copyFilesInDir(imageIdx, outputWarehouseDir, warehouseDir, images)
    if(Constants.GENERATE_KITTI):
        KITTIVelodyneIndx = copyFilesInDir(KITTIVelodyneIndx, KITTIVelodyneOutputDir, KITTIVelodyneDir, KITTIvelodyne)
        KITTIDepthIndx = copyFilesInDir(KITTIDepthIndx, KITTIDepthOutputDir, KITTIDepthDir, KITTIDepths)
        KITTIcalibIndx = copyFilesInDir(KITTIcalibIndx, KITTIcalibOutputDir, KITTIcalibDir, KITTICalibs)
        KITTILabelIndx = copyFilesInDir(KITTILabelIndx, KITTILabelOutputDir, KITTILabelDir, KITTILabels)
        KITTIImageIndx = copyFilesInDir(KITTIImageIndx, KITTIImageOutputDir, KITTIImageDir, KITTIImages)

labelIds = [i for i in range(labelIdx)]
train_split = labelIds[ : int(Constants.TRAIN_PERCENTAGE * len(labelIds))]
val_split = labelIds[int(Constants.TRAIN_PERCENTAGE * len(labelIds)) : ]
random.shuffle(train_split)
random.shuffle(val_split)
train_file = open(Constants.TRAIN_SPLIT, "w")
val_file = open(Constants.VAL_SPLIT, "w")
for i in train_split:
    train_file.write(str(i))
    if(i != train_split[-1]):
         train_file.write("\n")
for i in val_split:
    val_file.write(str(i))
    if(i != val_split[-1]):
         val_file.write("\n")

train_file.close()
val_file.close()
