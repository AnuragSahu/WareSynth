import os
import Constants
import sys

class FilePathManager(object):
    def __init__(self):
        
        self.datasetDumpDirectory = "./datasets/"
        self.sceneCaptureNumber = 0
        self.annotationWritingPath = None
        self.dataPointNumber = 0
        self.debugImageNumber = 0
        self.kittiImagePath = self.datasetDumpDirectory + "KITTI/image_2/"
        self.kittiLabelPath = self.datasetDumpDirectory + "KITTI/label_2/"
        self.kittiCalibpath = self.datasetDumpDirectory + "KITTI/calib/"
        self.kittiDepthPath = self.datasetDumpDirectory + "KITTI/depth/"
        self.kittiVelodynePath = self.datasetDumpDirectory + "KITTI/velodyne/"
        self.anuragAnnotationsPath = self.datasetDumpDirectory + "anuragAnnotations/"
        self.anuragAnnotationsLabelsPath = self.anuragAnnotationsPath + "labels/"
        self.anuragRGBImagesPath = self.anuragAnnotationsPath + "warehouse/"
        self.BoxProbValuesPath = self.anuragRGBImagesPath 
        self.anuragLayoutspath = None
        self.anuragLayoutDebugImagespath = self.datasetDumpDirectory + "debugOutputs/"
        self.layoutPath = None
        self.probabilityValue = None
        self.ensureDatasetDirectory()


    def ensureDatasetDirectory(self):
        try:
            os.mkdir(self.datasetDumpDirectory)
        except FileExistsError:
            pass
        try:
            os.makedirs(self.anuragAnnotationsLabelsPath)
        except FileExistsError:
            pass
        try:
            os.makedirs(self.anuragRGBImagesPath)
        except FileExistsError:
            pass
        try:
            os.makedirs(self.anuragLayoutDebugImagespath)
        except FileExistsError:
            pass
        if(Constants.GENERATE_KITTI):
            try:
                os.makedirs(self.kittiImagePath)
            except FileExistsError:
                pass
            try:
                os.makedirs(self.kittiLabelPath)
            except FileExistsError:
                pass
            try:
                os.makedirs(self.kittiCalibpath)
            except FileExistsError:
                pass
            try:
                os.makedirs(self.kittiDepthPath)
            except FileExistsError:
                pass
            try:
                os.makedirs(self.kittiVelodynePath)
            except FileExistsError:
                pass
        

    def capturedScene(self):
        self.sceneCaptureNumber += 1

    def LayoutsGenerated(self):
        self.sceneCaptureNumber += 1

    def getSceneCaptureNumber(self):
        return self.sceneCaptureNumber

    def getAnuragAnnotationsLabelPath(self):
        labelspath = self.anuragAnnotationsLabelsPath + str(self.sceneCaptureNumber).zfill(6)+".txt"
        return labelspath

    def getAnuragAnnotationsImagePath(self):
        imagePath = self.anuragRGBImagesPath + str(self.sceneCaptureNumber).zfill(6)+".png"
        return imagePath

    def getBoxLayoutPath(self):
        layoutPath = self.anuragRGBImagesPath + "box"+str(self.sceneCaptureNumber).zfill(6)+".png"
        return layoutPath

    def getShelfLayoutPath(self):
        layoutPath = self.anuragRGBImagesPath + "shelf"+str(self.sceneCaptureNumber).zfill(6)+".png"
        return layoutPath

    def getDebugRackLayoutPath(self, prefix, ID, shelf_number):
        layoutPath = self.anuragLayoutDebugImagespath + prefix +\
                     str(ID)[:-4].zfill(6) + ("_%s.png"%shelf_number)
        return layoutPath

    def updateDebugImageNumber(self):
        self.debugImageNumber += 1


filePathManager = FilePathManager()