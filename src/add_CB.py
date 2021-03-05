import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

class Add_CB():

    def __init__(self,CB_coords,CB_loc):
        self.CB_coords=CB_coords
        self.CB_loc=CB_loc

    def add_CB(self):

        subscript=0
        for coords in self.CB_coords:
            for obj in bpy.data.objects:
                obj.tag = True
            bpy.ops.import_scene.obj(filepath=self.CB_loc)
        #        bpy.ops.import_scene.obj(filepath=forklift_loc)

            for obj in bpy.data.objects:
                if obj.tag is False:
                    imported_object = obj

            name = imported_object.name
            print(name)
            bpy.data.objects[name].location.x += coords[0]
            bpy.data.objects[name].location.y += coords[1]
            bpy.data.objects[name].location.z += coords[2]
            bpy.data.objects[name].rotation_euler[2] = math.radians(270)
            subscript += 1
