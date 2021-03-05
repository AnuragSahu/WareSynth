# Counting Boxes

import cv2
import numpy as np
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join

dataset_path = "../../../test_images/top/"

files = [f for f in listdir(dataset_path) if isfile(join(dataset_path, f))]
files.sort()

# to find the number of boxes in the scene
for file in files:
    img = cv2.imread(join(dataset_path, file), 0)
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]  # ensure binary
    num_labels, labels_im = cv2.connectedComponents(img)
    number_of_boxes = num_labels - 1
    print(file, " : ", number_of_boxes)