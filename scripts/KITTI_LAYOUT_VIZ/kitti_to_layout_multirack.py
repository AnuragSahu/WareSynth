import os, sys
import glob
import pathlib
import numpy as np
import json
from PIL import Image, ImageDraw
import cv2
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

# Debug flag
Debug = True

# Define the Relative Paths

path = "./datasets/inputs/"
layout_dump_path = "./datasets/inputs/"
layout_Images_dump_path = "./datasets/output/"

image_center = [128, 128]
# final_image_size = 256
# processed_image_size = 512.0
maximum_number_racks = 4

try:
    os.mkdir(layout_Images_dump_path)
except FileExistsError:
    pass

def get_dimensions(dimensions):
    x = dimensions[2]
    y = dimensions[1]
    z = dimensions[0]
    return [x,y,z]

def get_locations(locations):
    x = locations[0]
    y = locations[2]
    z = locations[1]

    # print([x, y, z])
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

def generate_layout_rack(img_data, label,locations, dimentions, rotation_y, rack_number):
    imgs = img_data[0]
    res = img_data[1]
    length = img_data[2]
    width = img_data[3]

    center_x = int(float(locations[0]) / res + width / (2*res))
    # center_x = 256
    # center_y = int(float(locations[1]) / res + length / (2*res))
    center_y = int(float(locations[1]) / res)
    # center_y = 256
    
    # print("Rack: ", locations[0], center_x)

    orient = -1 * float(rotation_y)

    obj_w = int(float(dimentions[1])/res)
    obj_l = int(float(dimentions[0])/res)
    print("For Rack ",obj_w, obj_l)

    # rectangle = get_rect(center_x, center_y, obj_l, obj_w, orient)
    rectangle = get_rect(center_x, int(length/res) - center_y, obj_l, obj_w, orient)
    print("For Rack ",center_x, int(length/res) - center_y)
    
    draw = ImageDraw.Draw(imgs[rack_number])

    if (label == "Shelf"):
        draw.polygon([tuple(p) for p in rectangle], fill=255)
        print(center_x, center_y)

    imgs[rack_number] = imgs[rack_number].convert('L')
    

    return [imgs,res,length, width]

def generate_layout_boxes(img_data, label,locations, dimentions, rotation_y, rack_number):
    imgs = img_data[0]
    res = img_data[1]
    length = img_data[2]
    width = img_data[3]

    center_x = int(float(locations[0]) / res + width / (2*res))
    # center_y = int(float(locations[1]) / res + length / (2*res))
    center_y = int(float(locations[1]) / res)
    # center_y = 256

    # print("Box: ", locations[0], center_x)

    orient = -1 * float(rotation_y)

    obj_w = int(float(dimentions[1])/res)
    obj_l = int(float(dimentions[0])/res)
    print("For Box ",obj_w, obj_l)

    # rectangle = get_rect(center_x, center_y, obj_l, obj_w, orient)
    rectangle = get_rect(center_x, int(length/res) - center_y, obj_l, obj_w, orient)
    print("For Box ",center_x, int(length/res) - center_y)
    
    draw = ImageDraw.Draw(imgs[rack_number])

    if (label == "Box"):
        draw.polygon([tuple(p) for p in rectangle], fill=255)

    imgs[rack_number] = imgs[rack_number].convert('L')
    return [imgs,res,length, width]


for filename in glob.glob(os.path.join(path, '*.txt')):
    
    length = 16
    width = 16
    max_shelfs = 4
    max_boxes = max_shelfs
    res = length/256.0
    name = filename.split("/")[-1]
    image_center_rack = []
    image_center_box = []

    print("found-file")

    topView = np.zeros((int(length/res), int(width/res)))
    img = Image.fromarray(topView)
    boxes_imgs = [Image.fromarray(topView) for i in range(max_boxes)]
    boxes_img_data = [boxes_imgs, res, length, width]
    rack_imgs = [Image.fromarray(topView) for i in range(max_shelfs)]
    rack_img_data = [rack_imgs, res, length, width]

    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        lines = f.readlines()
        #print("Found File")
        for line in lines:
            labels = line.split()
            obj_type = labels[0]
            truncated = labels[1]
            occluded = labels[2]
            alpha = labels[3]
            bbox = labels[4:8]
            dimentions = get_dimensions(labels[8:11])
            location = get_locations(labels[11:14])
            rotation_y = labels[14]
            rack_number = int(labels[15])

            # print(obj_type)
            # print(rack_number)

            # print(image_center)

            if(obj_type == "Shelf"):
                #print("Got a shelf number : %d"%rack_number)
                image_center_rack.append([256, 256])
                rack_img_data = generate_layout_rack(rack_img_data, obj_type, location, dimentions, rotation_y, rack_number)
            
            if(obj_type == "Box"):
                image_center_box.append([256, 256])
                boxes_img_data = generate_layout_boxes(boxes_img_data, obj_type, location, dimentions, rotation_y, rack_number)

    final_layouts_racks = []

    for i in range(maximum_number_racks):
        if(i > len(rack_img_data[0])):
            pixels = np.zeros((int(length/res), int(width/res)))
        else:
            rack_img_data[0][i] = rack_img_data[0][i].rotate(0)
            pixels = list(rack_img_data[0][i].getdata())
            width, height = rack_img_data[0][i].size
            pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
            pixels = np.array(pixels)
        # xstart = image_center_rack[i][0]-int(final_image_size/2)
        # xend =  image_center_rack[i][0]+int(final_image_size/2)
        # ystart = int(image_center_rack[i][1])-int(final_image_size/2) 
        # yend = int(image_center_rack[i][1])+int(final_image_size/2)
        # pixels = pixels[ xstart:xend, ystart:yend ]
        if(Debug):
            file_path_0_1 = layout_Images_dump_path +"rack"+ name[:-4] + "_"+str(i)+".png"
            cv2.imwrite(file_path_0_1,pixels)
        final_layouts_racks.append(pixels)

    final_layouts_racks = np.array(final_layouts_racks)
    file_path = layout_dump_path +"rack"+ name[:-4] + ".npy"
#    np.save(file_path,final_layouts_racks)

    final_layouts_boxes = []
    for i in range(max_boxes):
        boxes_img_data[0][i] = boxes_img_data[0][i].rotate(0)
        pixels = list(boxes_img_data[0][i].getdata())
        width, height = boxes_img_data[0][i].size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        pixels = np.array(pixels)
        # xstart = image_center_box[i][0]-int(final_image_size/2)
        # xend =  image_center_box[i][0]+int(final_image_size/2)
        # ystart = int(image_center_box[i][1])-int(final_image_size/2) 
        # yend = int(image_center_box[i][1])+int(final_image_size/2)
        # pixels = pixels[ xstart:xend, ystart:yend ]

        if(Debug):
            file_path_0_1 = layout_Images_dump_path +"box"+ name[:-4] + "_"+str(i)+".png"
            cv2.imwrite(file_path_0_1,pixels)
            
        final_layouts_boxes.append(pixels)

    final_layouts_boxes = np.array(final_layouts_boxes)
    file_path = layout_dump_path +"box"+ name[:-4] + ".npy"
    np.save(file_path,final_layouts_boxes)

    # print(final_layouts_boxes.shape, final_layouts_racks.shape)

    for i in range(4):
        imageOut = np.zeros((256, 256))
        imageOut[final_layouts_racks[i] == 255] = 115
        imageOut[final_layouts_boxes[i] == 255] = 255

        file_path_0_1 = layout_Images_dump_path + "layout_" + str(i) + ".png"
        cv2.imwrite(file_path_0_1, imageOut)
    # print(final_layouts_racks[0])

print("\n\nGenerated the Layout at %s\n\n" % layout_dump_path)
