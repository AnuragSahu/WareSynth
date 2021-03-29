import bpy
from random import randrange
import random
import sys

def append_zero(num):
    return "." + str(num).zfill(3)

fire_ext_loc = './objects/primitives/Extinguisher/fire1.dae'

extinguisher_coords = [[10.5, 46.7, 2.5], [-10.5, 46.7, 2.5], [-10.5, -44.45, 2.5], [10.5, -44.45, 2.5]]

subscript = 0

model = "fire_ext"    

for coords in extinguisher_coords: 
    imported_object = bpy.ops.wm.collada_import(filepath=fire_ext_loc)
    change = append_zero(subscript)
    if subscript > 0:
        name = model + change
    else:
        name = model   

    bpy.data.objects[name].location.x += coords[0]
    bpy.data.objects[name].location.y += coords[1]
    bpy.data.objects[name].location.z += coords[2]

    subscript += 1

imported_object = bpy.ops.import_scene.obj(filepath='./objects/primitives/Extinguisher/fire1.obj')