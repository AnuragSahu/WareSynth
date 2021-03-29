import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

class Add_forklift():

    def __init__(self,forklift_coords,forklift_loc):
        self.forklift_loc = forklift_loc
        self.forklift_coords = forklift_coords

    def add_forklift(self):

        subscript = 0

        #for coords in extinguisher_coords:
        for coords in self.forklift_coords:
            for obj in bpy.data.objects:
                obj.tag = True
            #bpy.ops.wm.collada_import(filepath=forklift_loc)
            bpy.ops.import_scene.obj(filepath=self.forklift_loc)
        #        bpy.ops.import_scene.obj(filepath=forklift_loc)

            for obj in bpy.data.objects:
                if obj.tag is False:
                    imported_object = obj

            name = imported_object.name

            bpy.data.objects[name].location.x += coords[0]
            bpy.data.objects[name].location.y += coords[1]
            bpy.data.objects[name].location.z += coords[2]

            subscript += 1
