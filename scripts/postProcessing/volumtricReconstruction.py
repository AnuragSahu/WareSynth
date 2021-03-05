#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

show2dBB = False


def getBoundingBoxes(img):
    boundingBoxes = []
    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for cntr in contours:
        x,y,w,h = cv2.boundingRect(cntr)
        boundingBoxes.append([x,y,w,h])
    return boundingBoxes

def rackAndBoxBBs(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    boxThresh = cv2.threshold(gray,128,255,cv2.THRESH_BINARY)[1]
    boxBB = getBoundingBoxes(boxThresh)

    shelfThresh = cv2.threshold(gray,10,155,cv2.THRESH_BINARY)[1]
    rackBB = getBoundingBoxes(shelfThresh)
    
    return rackBB, boxBB

def getFreeSpace(rackBB, BoxBB):
    BoxBB.sort()
    # make the 3d and calculate Free space
    rackStarting_x = rackBB[0][0]

    freeSpaceBBoxs = []
    # get the free spaces from top view
    for boxes in BoxBB:
        freeSpaceBBoxTop_y = rackBB[0][1]
        freeSpaceBBoxTop_h = rackBB[0][3]
        freeSpaceBBoxTop_x = rackStarting_x
        freeSpaceBBoxTop_w = boxes[0] - rackStarting_x
        rackStarting_x = boxes[2] + boxes[0] #+ rackStarting_x
        freeSpaceBBoxs.append([freeSpaceBBoxTop_x,
                              freeSpaceBBoxTop_y,
                              freeSpaceBBoxTop_w,
                              freeSpaceBBoxTop_h])
    
    freeSpaceBBoxTop_x = rackStarting_x
    freeSpaceBBoxTop_y = rackBB[0][1]
    freeSpaceBBoxTop_w = rackBB[0][2] - rackStarting_x + rackBB[0][0]
    freeSpaceBBoxTop_h = rackBB[0][3]

    freeSpaceBBoxs.append([freeSpaceBBoxTop_x,
                          freeSpaceBBoxTop_y,
                          freeSpaceBBoxTop_w,
                          freeSpaceBBoxTop_h])
    
    return freeSpaceBBoxs


def scrutiniseFreeSpace(freeSpaceBBoxs):
    scrutinizedFreeSpaces = []
    for freeSpaceBBox in freeSpaceBBoxs:
        if(freeSpaceBBox[2] > 60): # free space thresholding
            scrutinizedFreeSpaces.append(freeSpaceBBox)
    return scrutinizedFreeSpaces

def stackBB(boxes, freeSpaces, freeSpacesAboveBoxes, rackBB):
    starting_height = 0
    for i in range(len(boxes)):
        for j in range(len(boxes[i])):
            boxes[i][j][1] += starting_height
        for j in range(len(freeSpaces[i])):
            freeSpaces[i][j][1] += starting_height
            height_increase = freeSpaces[i][j][4]*1.5
        for j in range(len(freeSpacesAboveBoxes[i])):
            freeSpacesAboveBoxes[i][j][1] += starting_height
        for j in range(len(rackBB[i])):
            rackBB[i][j][1] += starting_height
        starting_height -= height_increase
    return boxes, freeSpaces, freeSpacesAboveBoxes, rackBB

def getFreeSpacesAbove(rack, box):
    print(box, rack)
    free_x = box[0]
    free_y = box[1] # y of rack
    free_length = box[2] # length of box
    free_height = rack[1] - box[1]
    return [free_x, free_y, free_length, free_height]

def calculate3DBB(topBBox, frontBBox):
    Boxes = []

    for i in range(len(topBBox)):
        # length
        length = min(topBBox[i][2], frontBBox[i][2]) 
        # width
        width = topBBox[i][3]
        # height
        height = frontBBox[i][3]
        # x is towards right
        x = int(length/2) + max(topBBox[i][0], frontBBox[i][0])
        # y is upwards
        y = int(height/2) + frontBBox[i][1]
        # z is comming out of the image
        z = int(width/2) + topBBox[i][1]
        Boxes.append([x, y, z, length, width, height])
    
    return Boxes

def getBBForLabel(baseDatasetPath, layoutPath):
    #layout_number = "000580rackno_0.png"

    # find the bounding box for boxes in top view
    img = cv2.imread(baseDatasetPath+'top/'+layoutPath)
    top = img
    topRackBBox, topBoxesBBox = rackAndBoxBBs(img)
    topFreeSpaceBBoxs = getFreeSpace(topRackBBox, topBoxesBBox)
    topFreeSpaceBBoxs = scrutiniseFreeSpace(topFreeSpaceBBoxs)
    if(show2dBB):
        for freeSpaceBBox in topFreeSpaceBBoxs:
            cv2.rectangle(top,(freeSpaceBBox[0], freeSpaceBBox[1]), 
                        (freeSpaceBBox[0]+freeSpaceBBox[2], freeSpaceBBox[1]+freeSpaceBBox[3]),
                        (0,255,0))
        plt.imshow(top)

    # find the bounding box for boxes in front view
    img = cv2.imread(baseDatasetPath+'front/'+layoutPath)
    frontRackBBox, frontBoxesBBox = rackAndBoxBBs(img)
    front = img
    frontFreeSpaceBBoxs = getFreeSpace(frontRackBBox, frontBoxesBBox)
    frontFreeSpaceBBoxs = scrutiniseFreeSpace(frontFreeSpaceBBoxs)
    if(show2dBB):
        for freeSpaceBBox in frontFreeSpaceBBoxs:
            cv2.rectangle(front,(freeSpaceBBox[0], freeSpaceBBox[1]), 
                        (freeSpaceBBox[0]+freeSpaceBBox[2], freeSpaceBBox[1]+freeSpaceBBox[3]),
                        (0,255,0))
        plt.imshow(front)

    # find the empty spaces above the boxes
    freeSpaceAboveBoxs = []
    for box in frontBoxesBBox:
        freeSpaceAboveBox = getFreeSpacesAbove(frontRackBBox[0], box)
        freeSpaceAboveBoxs.append(freeSpaceAboveBox)
    if(show2dBB):
        for freeSpaceBBox in freeSpaceAboveBoxs:
            cv2.rectangle(front,(freeSpaceBBox[0], freeSpaceBBox[1]), 
                        (freeSpaceBBox[0]+freeSpaceBBox[2], freeSpaceBBox[1]+freeSpaceBBox[3]),
                        (0,255,0))
        plt.figure(figsize=(20,20))
        plt.imshow(front)

    return topRackBBox, topBoxesBBox, frontRackBBox, frontBoxesBBox,topFreeSpaceBBoxs, frontFreeSpaceBBoxs, freeSpaceAboveBoxs

rackBB = []
boxes = []
freeSpace = []
freeSpaceAboveBox = []
for i in range(3):
    topRackBBox, topBoxesBBox, frontRackBBox, frontBoxesBBox,topFreeSpaceBBoxs, \
    frontFreeSpaceBBoxs, freeFrontSpaceAboveBoxs = getBBForLabel('../../../test_images/', "004255rackno_"+str(i)+".png")
    freeSpaces3D = calculate3DBB(topFreeSpaceBBoxs, frontFreeSpaceBBoxs)
    freeSpacesAboveBoxes = calculate3DBB(topBoxesBBox, freeFrontSpaceAboveBoxs)
    Boxes = calculate3DBB(topBoxesBBox, frontBoxesBBox)
    rackBoundingBoxes = calculate3DBB(topRackBBox, frontRackBBox)
    boxes.append(Boxes)
    freeSpace.append(freeSpaces3D)
    freeSpaceAboveBox.append(freeSpacesAboveBoxes)
    rackBB.append(rackBoundingBoxes)

boxes, freeSpace, freeSpacesAboveBoxes, rackBB = stackBB(boxes, freeSpace, freeSpaceAboveBox, rackBB)

# plotting part
def get_cube(x,y,z, length, width, height):   
    phi = np.arange(1,10,2)*np.pi/4
    Phi, Theta = np.meshgrid(phi, phi)

    sx = np.cos(Phi)*np.sin(Theta)
    sy = np.sin(Phi)*np.sin(Theta)
    sz = np.cos(Theta)/np.sqrt(2)
    
    return sx, sy, sz

def makeCube(x,y,z,length, width, height, color, alpha):
    sx,sy,sz = get_cube(x,y,z, length, width, height)
    ax.plot_surface(sx*length + x, sy*height + y, sz*width + z, color = color, alpha = alpha)

fig = plt.figure(figsize=(20,20))
ax = fig.add_subplot(111, projection='3d')


scale = 512

# for freeSpaces3D in freeSpace:
#     for freeSpaces in freeSpaces3D:
#         x,y,z,length, width, height = freeSpaces
#         makeCube(x,y,z,length, width, height, 'g')

# for freeSpaces3D in freeSpacesAboveBoxes:
#    for freeSpaces in freeSpaces3D:
#        x,y,z,length, width, height = freeSpaces
#        makeCube(x,y,z,length, width, height, 'b')

boxes_color = ['g', 'r', 'c', 'm', 'y', 'k' ]


for Boxes in rackBB:
    for box in Boxes:
        x,y,z,length, width, height = box
        makeCube(x,y,z,length, width, height, 'y', 0.05)


for Boxes in boxes:
    for box in Boxes:
        x,y,z,length, width, height = box
        makeCube(x,y,z,length, width, height, [random.uniform(0,1),random.uniform(0,1),random.uniform(0,1)], 1)


ax.set_xlim(0,scale)
ax.set_ylim(0,scale)
ax.set_zlim(0,scale)
ax.set_aspect(1)
#plt.xlabel("X")
#plt.ylabel("Y")
ax.grid(False)
plt.axis('off')
ax.view_init(-90,-90)
plt.show()
