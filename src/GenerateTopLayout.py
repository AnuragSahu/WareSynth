import Constants
import numpy as np
import cv2
from PIL import Image, ImageDraw
from FileNameManager import filePathManager

class GenerateTopLayout(object):
    def __init__(self):
        self.length = Constants.LENGTH
        self.width = Constants.WIDTH
        self.layout_size = Constants.LAYOUT_SIZE
        self.res = self.length / self.layout_size
        self.DEBUG = True
        self.annotations = {}

    def writeLayout(self, annotations,  ID, dump_path):
        self.annotations = annotations
        shelf_layouts= []
        box_layouts = []
        min_shelf_number, max_shelf_number = self.get_shelf_range()
        for shelf_number in range(min_shelf_number, max_shelf_number+1):
            shelf, boxes = self.get_shelf_and_boxes(shelf_number)
            shelf, boxes = self.calculateCenter(shelf, boxes)
            shelf_layouts.append(self.getShelfLayout(shelf))
            box_layouts.append(self.getBoxesLayouts(boxes))
        self.write_layouts(shelf_layouts, box_layouts, ID, dump_path)
    
    def get_shelf_range(self):
        min_shelf = 99999999
        max_shelf = 0
        for annotation in self.annotations.values():
            if(annotation["shelf_number"] < min_shelf):
                min_shelf = annotation["shelf_number"]
            if(annotation["shelf_number"] > max_shelf):
                max_shelf = annotation["shelf_number"]
        return [min_shelf, max_shelf]
    
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

    def calculateCenter(self, shelf, boxes):
        center_x, center_y = shelf["location"][:2]
        shelf["center"][:2] = [0,0]
        for box in boxes:
            box_center_x, box_center_y = box["location"][:2]
            box["center"] = [float(box_center_x) - float(center_x), float(box_center_y)-float(center_y)]
        return [shelf, boxes]

    def getShelfLayout(self, shelf):
        layout = np.zeros(
            (int(self.length/self.res), 
            int(self.width/self.res))
        )
        layout = Image.fromarray(layout)
        layout =  self.getOneLayout(shelf,layout, 115)
        return self.accountCameraRotation(shelf["camera_rotation"], layout)

    def getBoxesLayouts(self, boxes):
        layout = np.zeros(
            (int(self.length/self.res), 
            int(self.width/self.res))
        )
        layout = Image.fromarray(layout)
        camera_layout = None
        for box in boxes:
            camera_layout = box["camera_rotation"]
            layout = self.getOneLayout(box, layout, 255)
        if(camera_layout != None): # rotate only if there is/are some boxes in the shelf
            layout = self.accountCameraRotation(camera_layout, layout)
        return layout

    def accountCameraRotation(self,camera_rotation, layout):
        layout = layout.rotate(float(camera_rotation[2]) * 180 / np.pi)
        return layout
    
    def getOneLayout(self,annotation, layout, fill):
        x,y = annotation["center"]
        center_x = int(float(x) / self.res + self.width / (2*self.res))
        center_y = int(float(y) / self.res + self.length / (2*self.res))
        orient = float(annotation["rotation_y"])
        dimensions = annotation["dimensions"]
        obj_w = int(float(dimensions[1])/self.res)
        obj_l = int(float(dimensions[0])/self.res)
        rectangle = self.get_rect(center_x, center_y, obj_l, obj_w, orient)
        draw = ImageDraw.Draw(layout)
        draw.polygon([tuple(p) for p in rectangle], fill=fill)
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

    def write_layouts(self, rack_layouts, box_layouts, ID, dump_path):
        final_layout_racks = []
        for shelf in range(Constants.MAX_SHELVES):
            #print(rack_layouts)
            if(shelf >= len(rack_layouts)):
                pixels = np.zeros((int(self.length/self.res), int(self.width/self.res)))
            else:
                pixels = list(rack_layouts[shelf].getdata())
                width, height = rack_layouts[shelf].size
                pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
                
                pixelsb = list(box_layouts[shelf].getdata())
                width, height = box_layouts[shelf].size
                pixelsb = [pixelsb[i * width:(i + 1) * width] for i in range(height)]
                

                for i in range(len(pixels)):
                    for j in range(len(pixels[i])):
                        if(pixelsb[i][j] != 255):
                            pixelsb[i][j] = pixels[i][j]
                pixels = np.array(pixelsb)    

            if(self.DEBUG):
                cv2.imwrite(filePathManager.getDebugRackLayoutPath("top",ID, shelf), pixels)
                filePathManager.updateDebugImageNumber()
            final_layout_racks.append(pixels)
        final_layout_racks = np.array(final_layout_racks)
        file_path = dump_path +"top"+ ID[:-4] + ".npy"
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
        #         cv2.imwrite(filePathManager.getDebugRackLayoutPath("topBox",ID, shelf), pixels)
        #         filePathManager.updateDebugImageNumber()
        #     final_layouts_boxes.append(pixels)
        # final_layouts_boxes = np.array(final_layouts_boxes)
        # file_path = dump_path +"topBox"+ ID[:-4] + ".npy"
        # np.save(file_path,final_layouts_boxes)
    
        #np.save(dump_path +"height"+ ID[:-4] + ".npy",shelfHeightDifference)
generateTopLayout = GenerateTopLayout()