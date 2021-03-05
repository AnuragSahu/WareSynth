from FileNameManager import filePathManager
import Constants
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps

class GenerateFrontalLayout(object):
    def __init__(self):
        self.length = Constants.LENGTH
        self.width = Constants.WIDTH
        self.layout_size = Constants.LAYOUT_SIZE
        self.res = self.length / self.layout_size
        self.DEBUG = True
        self.annotations = {}

    def writeLayout(self, annotations, ID, dump_path):
        self.annotations = annotations
        min_shelf_number, _ = self.get_shelf_range()
        shelf_layouts = []
        box_layouts = []
        min_shelf_number, max_shelf_number = self.get_shelf_range()
        #interShelfDistance = self.annotations["intershelfDistance"] #self.getInterShelfDistance()
        for shelf_number in range(min_shelf_number, max_shelf_number+1):
            #interShelfDistance = self.annotations["intershelfDistance"]
            shelf, boxes = self.get_shelf_and_boxes(shelf_number)
            interShelfDistance = float(shelf["interShelfDistance"])
            _, centerX , centerY = shelf["location"]
            camera_rotation_z = shelf["camera_rotation"][2]
            layout_shelf = self.generateFrontalLayoutShelf(shelf, centerX , centerY, interShelfDistance)
            layout_shelf = self.accountCameraRotation(layout_shelf, camera_rotation_z)
            shelf_layouts.append(layout_shelf)

            layout_box = self.generateFrontalLayoutBoxes(boxes, centerX, centerY)
            layout_box = self.accountCameraRotation(layout_box, camera_rotation_z)
            box_layouts.append(layout_box)
        self.write_layouts(shelf_layouts, box_layouts, interShelfDistance, ID, dump_path)

    def generateFrontalLayoutShelf(self, annotation, img_x, img_y, obj_w):
        layout = np.zeros(
            (int(self.length/self.res), 
            int(self.width/self.res))
        )
        layout = Image.fromarray(layout)
        _,x,y = annotation["location"]
        center_x = int((float(x)-float(img_x)) / self.res + self.width / (2*self.res))
        center_y = int((float(img_y)-float(y) - obj_w/2) / self.res + self.length / (2*self.res))
        orient = 0
        dimensions = annotation["dimensions"]
        print("FREE SPACE : ", obj_w)
        obj_w = int((float(obj_w) + 0.05)/self.res)
        obj_l = int(float(dimensions[0])/self.res)
        rectangle = self.get_rect(center_x, center_y, obj_l, obj_w, orient)
        draw = ImageDraw.Draw(layout)
        draw.polygon([tuple(p) for p in rectangle], fill = 115)
        layout = layout.convert('L')
        return layout

    def accountCameraRotation(self, layout, camera_rotation):
        if(float(camera_rotation) > np.pi):
            layout = ImageOps.mirror(layout)
        return layout

    def generateFrontalLayoutBoxes(self, annotations, img_x, img_y):
        layout = np.zeros(
            (int(self.length/self.res), 
            int(self.width/self.res))
        )
        layout = Image.fromarray(layout)
        for annotation in annotations:
            _,x,y = annotation["location"]
            center_x = int((float(x)-float(img_x)) / self.res + self.width / (2*self.res))
            center_y = int((float(img_y)-float(y)) / self.res + self.length / (2*self.res))
            orient = 0
            dimensions = annotation["dimensions"]
            print("BOX",dimensions[2])
            obj_w = int(float(dimensions[2])/self.res)
            obj_l = int(float(dimensions[1])/self.res)
            rectangle = self.get_rect(center_x, center_y, obj_l, obj_w, orient)
            draw = ImageDraw.Draw(layout)
            draw.polygon([tuple(p) for p in rectangle], fill = 255)
            layout = layout.convert('L')
        return layout

    def get_rect(self, x, y, width, height, theta):
        rect = np.array([(-width / 2, -height / 2), (width / 2, -height / 2),
                         (width / 2, height / 2), (-width / 2, height / 2),
                         (-width / 2, -height / 2)])

        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

        offset = np.array([x, y])
        transformed_rect = np.dot(rect, R) + offset
        return transformed_rect

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

    def write_layouts(self, rack_layouts, box_layouts, shelfHeightDifference, ID, dump_path):
        final_layout_racks = []
        for shelf in range(Constants.MAX_SHELVES):
            if(shelf >= len(rack_layouts)):
                pixels = np.zeros((int(self.length/self.res), int(self.width/self.res)))
            else:
                pixels = list(rack_layouts[shelf].getdata())
                width, height = rack_layouts[shelf].size
                pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
                pixels = np.array(pixels)

                pixelsb = list(box_layouts[shelf].getdata())
                width, height = box_layouts[shelf].size
                pixelsb = [pixelsb[i * width:(i + 1) * width] for i in range(height)]
                

                for i in range(len(pixels)):
                    for j in range(len(pixels[i])):
                        if(pixelsb[i][j] != 255):
                            pixelsb[i][j] = pixels[i][j]
                pixels = np.array(pixelsb)    


            if(self.DEBUG):
                cv2.imwrite(filePathManager.getDebugRackLayoutPath("front",ID, shelf), pixels)
                filePathManager.updateDebugImageNumber()
            final_layout_racks.append(pixels)
        final_layout_racks = np.array(final_layout_racks)
        file_path = dump_path +"front"+ ID[:-4] + ".npy"
        np.save(file_path, final_layout_racks)

        # final_layouts_boxes = []
        # for shelf in range(Constants.MAX_SHELVES):
        #     #boxes_img_data[0][i] = boxes_img_data[0][i].rotate(180)
        #     if(shelf >= len(box_layouts)):
        #         pixels = np.zeros((int(self.length/self.res), int(self.width/self.res)))
        #     else:
        #         pixels = list(box_layouts[shelf].getdata())
        #         width, height = box_layouts[shelf].size
        #         pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        #         pixels = np.array(pixels)
        #     if(self.DEBUG):
        #         cv2.imwrite(filePathManager.getDebugRackLayoutPath("frontBox",ID, shelf), pixels)
        #         filePathManager.updateDebugImageNumber()
        #     final_layouts_boxes.append(pixels)
        # final_layouts_boxes = np.array(final_layouts_boxes)
        # file_path = dump_path +"frontBox"+ ID[:-4]+ ".npy"
        # np.save(file_path,final_layouts_boxes)
    
        np.save(dump_path +"height"+ ID[:-4] + ".npy",shelfHeightDifference)

generateFrontalLayout = GenerateFrontalLayout()