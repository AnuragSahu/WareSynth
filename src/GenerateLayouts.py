from os.path import join
from glob import glob
import Constants
import numpy as np
from FileNameManager import filePathManager
from GenerateTopLayout import generateTopLayout
from GenerateFrontalLayout import generateFrontalLayout

class GenerateLayouts(object):
    def __init__(self):
        self.annotations = {}

    def read_annotations(self, annotationsPath, dump_path):
        for file in glob(join(annotationsPath, '*.txt')):
            ID = file.split("/")[-1]
            print("For ID : ",ID)
            f = open(file, "r")
            annotationLines = f.readlines()
            annotationID = 0
            self.max_shelf_number = 0
            self.annotations = {}
            for annotationLine in annotationLines:
                labels = annotationLine.split(", ")
                object_type = labels[0]
                shelf_number = int(labels[1])
                location = labels[2:5]
                orientation = labels[5:8]
                rotation_y = labels[7]
                dimensions = labels[8:11]
                scale = labels[11:14]
                camera_rotation = labels[17:21]
                interShelfDistance = labels[23]

                self.annotations[annotationID] = {
                    "object_type" : object_type,
                    "shelf_number" : shelf_number,
                    "location" : location,
                    "orientation" : orientation,
                    "rotation_y" : rotation_y,
                    "scale" : scale,
                    "dimensions" : dimensions,
                    "camera_rotation" : camera_rotation,
                    "center" : [0,0],
                    "interShelfDistance" : interShelfDistance
                }
                if(shelf_number > self.max_shelf_number):
                    self.max_shelf_number = shelf_number
                annotationID += 1
    
            #generateFrontalLayout.writeLayout(self.annotations)
            generateTopLayout.writeLayout(self.annotations, ID, dump_path)
            generateFrontalLayout.writeLayout(self.annotations, ID, dump_path)
            
    def get_shelf_and_boxes(self, shelfNumber):
        shelf = None
        boxes = []
        for annotation in self.annotations.values():
            if(annotation["shelf_number"] == shelfNumber):
                if(annotation["object_type"] == "Shelf"):
                    shelf = annotation
                elif(annotation["object_type"] == "Box"):
                    boxes.append(annotation)
        return [shelf,boxes]

    def getInterShelfDistance(self):
        min_shelf, _ = self.get_shelf_range()
        shelf_1, shelf_2 = min_shelf, min_shelf+1
        if(shelf_1 == None or shelf_2 == None):
            shelfHeightDifference = Constants.MAX_SHELF_DIFF_VAL
        else:
            bottomShelfAnnotation,_ = self.get_shelf_and_boxes(shelf_1)
            topShelfAnnotation,_ = self.get_shelf_and_boxes(shelf_2)
            heightOfBottomShelf = bottomShelfAnnotation["location"][2]
            heightOftopShelf = topShelfAnnotation["location"][2]
            shelfHeightDifference = abs(float(heightOftopShelf) - float(heightOfBottomShelf))
            print(shelfHeightDifference)
        return shelfHeightDifference



    def get_shelf_range(self):
        min_shelf = 99999999
        max_shelf = 0
        for annotation in self.annotations.values():
            if(annotation["shelf_number"] < min_shelf):
                min_shelf = annotation["shelf_number"]
            if(annotation["shelf_number"] > max_shelf):
                max_shelf = annotation["shelf_number"]

        return [min_shelf, max_shelf]

if __name__ == "__main__":
    generatelayouts = GenerateLayouts()
    generatelayouts.read_annotations(
        filePathManager.anuragAnnotationsLabelsPath,
        filePathManager.anuragRGBImagesPath
    )
    print("Generated Layouts at : ",filePathManager.anuragRGBImagesPath)
