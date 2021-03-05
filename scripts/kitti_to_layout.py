import os
import glob
import pathlib
import numpy as np
import json
from PIL import Image, ImageDraw
import cv2
import matplotlib.pyplot as plt

# Debug flag
Debug = True

# Define the Relative Paths
dataset_name = "KITTI"
path_to_dataset = "../datasets/"
path_to_label_file = "label_2/"
path_to_calib_file = "calib/"
path = path_to_dataset + dataset_name + "/" + path_to_label_file

generated_Dataset_name = "layouts"

layout_image_dump_path = path_to_dataset + generated_Dataset_name + "/" + dataset_name + "/"

# Check if the directory exists



def get_dimensions(dimensions):
    x = dimensions[2]
    y = dimensions[1]
    z = dimensions[0]
    return [x,y,z]

def get_rect(x, y, width, height, theta):
    rect = np.array([(-width / 2, -height / 2), (width / 2, -height / 2),
                     (width / 2, height / 2), (-width / 2, height / 2),
                     (-width / 2, -height / 2)])

    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])

    offset = np.array([x, y])
    transformed_rect = np.dot(rect, R) + offset

    return transformed_rect

def generate_layout(img_data, label,locations, dimentions, rotation_y):

    img = img_data[0]
    res = img_data[1]
    length = img_data[2]
    width = img_data[3]

    center_x = int(float(locations[0]) / res + width / (2*res))
    center_y = int(float(locations[1]) / res + length / (2*res))

    orient = -1 * float(rotation_y)

    obj_w = int(float(dimentions[1])/res)
    obj_l = int(float(dimentions[0])/res)

    rectangle = get_rect(
                center_x, int(length / res) - center_y, obj_l, obj_w, orient)
    
    draw = ImageDraw.Draw(img)

    if (label == "Box"):
        draw.polygon([tuple(p) for p in rectangle], fill=255)

    if (label == "Shel"):
        draw.polygon([tuple(p) for p in rectangle], fill=115)

    img = img.convert('L')
    

    return [img,res,length, width]


for filename in glob.glob(os.path.join(path, '*.txt')):
    
    length = 16
    width = 16
    res = length/256.0
    name = filename.split("/")[-1]

    topView = np.zeros((int(length/res), int(width/res)))
    img = Image.fromarray(topView)
    img_data = [img, res, length, width]
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        lines = f.readlines()
        for line in lines:
            labels = line.split()
            obj_type = labels[0]
            truncated = labels[1]
            occluded = labels[2]
            alpha = labels[3]
            bbox = labels[4:8]
            dimentions = get_dimensions(labels[8:11])
            location = labels[11:14]
            rotation_y = labels[14]
            img_data = generate_layout(img_data, obj_type, location, dimentions, rotation_y)

    file_path = layout_image_dump_path + name[:-4] + ".png"
    
    img_data[0].save(file_path)

print("\n\nGenerated the Layout at %s\n\n" % layout_image_dump_path)