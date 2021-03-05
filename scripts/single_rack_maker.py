import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

from math import *
from mathutils import Matrix,Vector
import os

sys.path.append(os.path.relpath("/home/shell_basher/Honors/synthetic_warehouse/scripts/pillared_warehouse/"))
print(os.getcwd())

class Place_racks_and_objects():


    def __init__(self,subscript,prob_of_box,rack_loc,all_box_loc,z_positions,y_positions,box_count,offset_x,x_coord,y_coord,z,num_section_y,corridor_y,shelf_count):
        self.subscript = subscript
        self.rack_loc = rack_loc
        self.all_box_loc = all_box_loc
        self.z_positions = z_positions
        self.y_positions = y_positions
        self.prob_of_box = prob_of_box
        self.box_count = box_count
        self.offset_x = offset_x
        self.x_coord=x_coord
        self.y_coord=y_coord
        self.z=z
        self.num_section_y=num_section_y
        self.corridor_y=corridor_y
        self.shelf_count=shelf_count


    def append_zero(self,num):
        return "." + str(num).zfill(3)

    def place_racks_and_objects(self,rack_location,subscript,count):

        change = self.append_zero(subscript)
        bpy.ops.object.add(radius=1.0, type='EMPTY', enter_editmode=False, align='WORLD', location=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0])
    
        if subscript > 0:
            bpy.data.objects['Empty'].name = 'Rack' + change
        else:
            bpy.data.objects['Empty'].name = 'Rack'

        model = "Rack"
        if subscript > 0:
            name = model + change
        else:
            name = model
    
        number = 0
        for i in range(1):
            submodel = "Shelf"
            change = self.append_zero(subscript*1 + number)
            if number > 0:
                subname = submodel + change
            else:
                subname = submodel
            imported_object = bpy.ops.wm.collada_import(filepath=self.rack_loc)
            bpy.ops.transform.translate(value=(rack_location[0]/2, rack_location[1]/2, i*1.29/2), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.data.objects[subname].parent = bpy.data.objects[name]

            number += 1

        boxes = ["BoxB","BoxA", "BoxC","BoxH"]
        prev_model=None
        for rows in range(1):
            for cols in self.y_positions:
                if  random.randint(0,1) <= self.prob_of_box:
                    model = random.choice(boxes)
                    model_temp = model
        #            model = model+(append_zero(box_count[model_temp]))
        
                    change = self.append_zero(self.box_count[model_temp])
                    if self.box_count[model_temp] > 0:
                        model = model + change
                    else:
                        model = model
        
                    self.box_count[model_temp] += 1
                    final_model_location = self.all_box_loc + model_temp + "/model2.dae"
                    print(final_model_location)
                    imported_object = bpy.ops.wm.collada_import(filepath=final_model_location)
                    obj = bpy.data.objects[model]
                    rot_mat = Matrix.Rotation(radians(random.randint(0, 45)), 4, 'Z')
                    orig_loc, orig_rot, orig_scale = obj.matrix_world.decompose()
                    print(orig_loc)
                    orig_loc_mat = Matrix.Translation(orig_loc)
                    print(Vector((10, 10, 10)))
                    orig_rot_mat = orig_rot.to_matrix().to_4x4()
                    orig_scale_mat = np.dot(np.dot(Matrix.Scale(orig_scale[0],4,(1,0,0)),Matrix.Scale(orig_scale[1],4,(0,1,0))),Matrix.Scale(orig_scale[2],4,(0,0,1)))
                    obj.matrix_world = np.dot(orig_loc_mat,np.dot(rot_mat,np.dot(orig_rot_mat,orig_scale_mat)))
                    # bpy.ops.transform.translate(value=((self.offset_x), (cols ), (rows + rack_location[2])), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    bpy.data.objects[model].location.x = self.offset_x+ rack_location[0]
                    bpy.data.objects[model].location.y = cols + rack_location[1]
                    bpy.data.objects[model].location.z = rows*1.29 + 0.35
                    prev_model = model

    def add_racks_boxes(self):
        for i in range(1):
            count=0
            for j in range(1):
                 # if  x>0 and y>-8 :
                 #     pass
                 # else:
                count+=1
                print("THE COUNT OF THE RACK IS")
                print(count)
                model = "Rack Model"
                # count += 1
                change = self.append_zero(self.subscript)
                if self.subscript > 0:
                    name = model + change
                else:
                    name = model

                self.place_racks_and_objects([0, 0, self.z], self.subscript,count)

                self.subscript += 1


prob_of_box = 0.5

corridor_y = 1

num_section_y = 1

all_box_loc = '/home/shell_basher/Honors/synthetic_warehouse/objects/primitives/boxes_avinash/'
rack_loc = '/home/shell_basher/Honors/synthetic_warehouse/objects/primitives/Racks/rack_modular2.dae'

offset_x = -0.5
z_positions = []
y_positions = [-2.3, -1.2, 0, 1.5]

box_count = {"BoxA":0, "BoxB":0, "BoxC":0, "BoxD":0, "BoxF":0, "BoxG":0, "BoxH":0, "BoxI":0}


z = -1.29

x_coord = []
y_coord = []

subscript = 0

racks_boxes = Place_racks_and_objects(subscript,prob_of_box,rack_loc,all_box_loc,z_positions,y_positions,box_count,offset_x,x_coord,y_coord,z,num_section_y,corridor_y,1)
racks_boxes.add_racks_boxes()
