import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

class Add_fire_ext():
    def __init__(self,extinguisher_coords,fire_ext_loc,subscript):
        self.extinguisher_coords=extinguisher_coords
        self.fire_ext_loc=fire_ext_loc
        self.subscript=subscript

    def add_fire_ext(self):

        self.subscript = 0
        model = "fire_ext_10285_Fire_Extinguisher_v3_iterations-2"

        for coords in self.extinguisher_coords:

            for obj in bpy.data.objects:
                obj.tag = True

            bpy.ops.import_scene.obj(filepath=self.fire_ext_loc)

            for obj in bpy.data.objects:
                if obj.tag is False:
                    imported_object = obj

            name = imported_object.name

            bpy.data.objects[name].location.x += coords[0]
            bpy.data.objects[name].location.y += coords[1]
            bpy.data.objects[name].location.z += coords[2]

            self.subscript += 1
