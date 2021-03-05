# import required image module
from PIL import Image
from os import listdir
from os.path import isfile, join
from pathlib import Path

imagesPath = "./datasets/anuragAnnotations/depth/"
flippedImagesPath = "./datasets/anuragAnnotations/depthFlipped/"

images = [f for f in listdir(imagesPath) if isfile(join(imagesPath, f))]
images.sort()

for image in images:
    imageObject = Image.open(join(imagesPath, image))
    hori_flippedImage = imageObject.transpose(Image.FLIP_LEFT_RIGHT)
    hori_flippedImage = hori_flippedImage.save(join(flippedImagesPath, image))
