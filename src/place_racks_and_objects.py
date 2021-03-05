import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
from Console import log
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from Assets import assets
from CameraProperties import cameraProperties
from FileNameManager import filePathManager



class Place_racks_and_objects():


    def __init__(self,subscript,prob_of_box,rack_loc,shelf_loc,support_loc,reference_line_up_loc,reference_line_down_loc,all_box_loc,box_count,x_coord,y_coord,z,num_section_y,corridor_y,shelf_count, cli,rack_lengths,rack_heights,pallet_loc):
        self.subscript = subscript
        self.rack_loc = rack_loc
        self.shelf_loc = shelf_loc
        self.support_loc = support_loc
        self.all_box_loc = all_box_loc
        self.prob_of_box = prob_of_box
        self.box_count = box_count
        self.reference_line_up_loc = reference_line_up_loc
        self.reference_line_down_loc = reference_line_down_loc
        self.x_coord=x_coord
        self.y_coord=y_coord
        self.z=z
        self.num_section_y=num_section_y
        self.corridor_y=corridor_y
        self.shelf_count=shelf_count
        self.cli = cli
        self.rack_lengths = rack_lengths
        self.rack_heights = rack_heights
        self.pallet_loc = pallet_loc
        self.shelf_num = 0

        self.rack_to_shelf = {}
        self.shelf_to_box = {}
        self.box_properties = {}
        self.shelf_properties = {}
        self.invisible_lines_properties = {}
        self.light = []

    def append_zero(self,num):
        return "." + str(num).zfill(3)

    def place_box(self,model,x,y,z,rot_angle, shelf, row_num, rack_num, height_shelf, boxes_dim):
        model_temp = model
        z = z + 0.32 + boxes_dim[model][2]/2 
        z_increment = boxes_dim[model][2] 
        if model == "BoxI":
            z += 0.09
        # if model == "BoxA":
        #     z_increment -= 2*0.04788
        #     z -= 0.04788s

        curr_z = z 
        while(random.uniform(0,1) <= self.prob_of_box and curr_z + z_increment/2 < height_shelf):
            rot_angle = random.uniform(-5,5)
            model = model_temp
            change = self.append_zero(self.box_count[model_temp])
            if self.box_count[model_temp] > 0:
                model = model + change
            else:
                model = model
            self.shelf_to_box[shelf].append(model)
            
            self.box_count[model_temp] += 1
            final_model_location = self.all_box_loc + model_temp + "/model.dae"
            bpy.ops.wm.collada_import(filepath=final_model_location)
            obj = bpy.data.objects[model]
            rot_mat = Matrix.Rotation(radians(rot_angle), 4, 'Z')
            orig_loc, orig_rot, orig_scale = obj.matrix_world.decompose()
            orig_loc_mat = Matrix.Translation(orig_loc)
            orig_rot_mat = orig_rot.to_matrix().to_4x4()
            orig_scale_mat = np.dot(np.dot(Matrix.Scale(orig_scale[0],4,(1,0,0)),Matrix.Scale(orig_scale[1],4,(0,1,0))),Matrix.Scale(orig_scale[2],4,(0,0,1)))
            obj.matrix_world = np.dot(orig_loc_mat,np.dot(rot_mat,np.dot(orig_rot_mat,orig_scale_mat)))
            
            bpy.ops.transform.translate(value=(x, y, curr_z), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.data.objects[model]["category_id"] = 1
            
            self.box_properties[model] = self.set_properties(model, row_num, rack_num)
            # prev_model = model
            curr_z += z_increment

    def set_properties(self, model, row_num, rack_num):
        obj = bpy.data.objects[model]
        temp = []
        temp.append([obj.location[0], obj.location[1], obj.location[2]])
        temp.append([obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]])
        temp.append([obj.scale[0], obj.scale[1], obj.scale[2]])
        temp.append([obj.dimensions[0], obj.dimensions[1], obj.dimensions[2]])
        temp.append([row_num, rack_num])

        return temp

    def place_racks_and_objects(self,rack_location,subscript,no_of_shelves,len_shelf,height_shelf,boxes_dim, rack_num, boxes):


        change = self.append_zero(subscript)
        bpy.ops.object.add(radius=1.0, type='EMPTY', enter_editmode=False, align='WORLD', location=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0])
        
        number = 0
        for i in range(no_of_shelves):
            shelf = "Shelf"
            line_up = "LineUp"
            line_down = "LineDown"
            support = "Support"
            change = self.append_zero(self.shelf_num)
            if self.shelf_num > 0:
                shelf = shelf + change
                line_up = line_up + change
                line_down = line_down + change
                support = support + change
            self.shelf_num += 1

            self.rack_to_shelf[rack_num].append(shelf)
            self.shelf_to_box[shelf] = []

            bpy.ops.wm.collada_import(filepath=self.shelf_loc)
            if self.cli:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1], 0.32 + 1.32 * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)   
            else:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1],0.30*(height_shelf/1.31)*i + (height_shelf/1.31)*i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                log("shelf height"+str(0.30*(height_shelf/1.31)*i + (height_shelf/1.31)*i))
                log(str(height_shelf))
            bpy.ops.transform.resize(value=(1,len_shelf/5.12,1))
            
            bpy.ops.wm.collada_import(filepath=self.support_loc)
            if self.cli:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1], 0.62 + 1.31 * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)   
            else:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1],0.30*(height_shelf/1.31)*i +((height_shelf/1.31)-1)*0.28 + (height_shelf/1.31) * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.transform.resize(value=(1,len_shelf/5.12,height_shelf/1.31))



            #upper bound invisible object
            bpy.ops.wm.collada_import(filepath=self.reference_line_up_loc)
            if self.cli:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1], 0.62 + 1.31 * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)   
            else:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1],0.30*(height_shelf/1.31)*i +((height_shelf/1.31)-1)*0.28 + (height_shelf/1.31) * i + 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.transform.resize(value=(1,len_shelf,1))

            self.invisible_lines_properties[line_up] = self.set_properties(line_up, i, rack_num)


            #lower bound invisible
            bpy.ops.wm.collada_import(filepath=self.reference_line_down_loc)
            if self.cli:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1], 0.62 + 1.31 * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)   
            else:
                bpy.ops.transform.translate(value=(rack_location[0], rack_location[1],0.30*(height_shelf/1.31)*i +((height_shelf/1.31)-1)*0.28 + (height_shelf/1.31) * i + 0.65), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.transform.resize(value=(1,len_shelf,1))

            self.invisible_lines_properties[line_down] = self.set_properties(line_down, i, rack_num)

            self.shelf_properties[shelf] = self.set_properties(shelf, i, rack_num)

            
        prev_model=None
        thresh = 0.3
        for rows in range(no_of_shelves):

            len_rack = len_shelf
            rack_start = -len_rack/2
            rack_end = len_rack/2
            model = random.choice(boxes)
            dim_box = boxes_dim[model]
            box_x = dim_box[0]
            box_y = dim_box[1]
            ht_adj = dim_box[2]
            # rot_angle = random.uniform(-0.5,0.5)
            rot_angle = 5
            
            curr_boxy = 0
            curr_protrusion = 0

            next_protrusion = abs((rot_angle/90))* (box_x/2-box_y/2)
            next_boxy =  box_y/2

            yloc_curr = rack_start
            yloc_next = yloc_curr + curr_boxy + curr_protrusion + thresh + next_boxy + next_protrusion
            
            while(yloc_next + next_boxy <= (rack_end-thresh)):

                curr_boxy = next_boxy
                curr_protrusion = next_protrusion
                yloc_curr = yloc_next
                # bpy.ops.wm.collada_import(filepath=self.pallet_loc)
                # bpy.ops.transform.resize(value=(box_x/1.57,box_y/0.763,1))
                # bpy.ops.transform.translate(value=(rack_location[0], 0.092 + rack_location[1],0.30*(height_shelf/1.31)*i +((height_shelf/1.31)-1)*0.28 + (height_shelf/1.31) * i), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                # self.place_box(model,rack_location[0],yloc_curr + rack_location[1], 0.30*(height_shelf/1.31)*rows +((height_shelf/1.31)-1)*0.28 + (height_shelf/1.31) * rows,rot_angle)
                self.place_box(model,rack_location[0],yloc_curr + rack_location[1], 0.30*(height_shelf/1.31)*rows + (height_shelf/1.31)*rows,rot_angle, self.rack_to_shelf[rack_num][rows], rows, rack_num, height_shelf*(rows+1), boxes_dim)

                model = random.choice(boxes)
                dim_box = boxes_dim[model]
                box_x = dim_box[0]
                box_y = dim_box[1]
                ht_adj = dim_box[2]

                # rot_angle = random.uniform(-5,5)
                rot_angle = 5


                next_protrusion = abs((rot_angle/90))* (box_x/2-box_y/2)
                next_boxy =  box_y/2
                yloc_next = yloc_curr + curr_boxy + curr_protrusion + thresh + next_boxy + next_protrusion
         
    def reSetMatrices(self):
        self.rack_to_shelf = {}
        self.shelf_to_box = {}
        self.box_properties = {}
        self.shelf_properties = {}
        self.invisible_lines_properties = {}


    def add_racks_boxes(self):
        shelves = random.randrange(self.shelf_count[0], self.shelf_count[1])
        boxes_dim = {
            "BoxA" : [0.939, 0.725, 0.763],
            "BoxB" : [0.830277, 1.10002, 0.620674],
            "BoxC" : [0.993878, 1.37, 0.581966],
            "BoxD" : [1, 0.9, 0.581966],
            "BoxE" : [0.74, 0.8, 0.6],
            "BoxF" : [0.919, 0.876, 0.809457],
            "BoxG" : [0.9, 1.0, 0.5],
            "BoxH" : [0.8, 0.8, 0.4],
            "BoxI" : [0.96719, 1.19178, 0.936],
            "CrateA" : [1.32, 0.879998, 0.48726],
            "CrateB" : [1.32, 1.68, 0.399],
            # "CrateC" : [0.6, 0.8, 0.443],
        }

        box_groups = []
        box_groups.append(["BoxA","BoxC", "BoxD", "BoxF", "BoxG", "BoxH","CrateA", "CrateB","CrateA", "CrateB"])  # Boxes G and H may be too small
        # box_groups.append([])

        rack_num = 0
        for i in range(len(self.x_coord)):
            if i%2 == 0: #because two are joined
                shelves = random.randrange(self.shelf_count[0], self.shelf_count[1])
            # print(self.shelf_count)
            #print(shelves)
            for j in range(len(self.y_coord)):

                self.rack_to_shelf[rack_num] = []
                
                model = "Rack Model"
                # count += 1
                change = self.append_zero(self.subscript)
                if self.subscript > 0:
                    name = model + change
                else:
                    name = model

                self.place_racks_and_objects([self.x_coord[i], self.y_coord[j], self.z], self.subscript, shelves,self.rack_lengths[j],self.rack_heights[j],boxes_dim, rack_num, box_groups[0])#random.randint(0,1)
                self.subscript += 1
                rack_num += 1
        
        assets.set_dict(self.rack_to_shelf, self.shelf_to_box, self.box_properties, self.shelf_properties, self.invisible_lines_properties)