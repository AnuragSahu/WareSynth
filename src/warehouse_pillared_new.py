import cv2
import bpy
import bpycv
from random import randrange
import random
import sys
from math import *
from mathutils import Matrix,Vector
import numpy as np
import random
from mathutils.bvhtree import BVHTree
import math
import sys
import os
sys.path.append(os.path.relpath("./scripts/pillared_warehouse/"))
print(os.getcwd())
from place_racks_and_objects import Place_racks_and_objects
from add_forklift import Add_forklift
from add_CB import Add_CB
from add_fire_ext import Add_fire_ext
import mathutils
import time
import Constants
from CameraProperties import cameraProperties
from GenerateAnnotations import generateAnnotations 
from Assets import assets
from Console import log, clearLog
from FileNameManager import filePathManager
from FOV import fov
from WipeOutObject import deleteSelectedObjects
from WriteKitti import writeKitti

clearLog()
filePathManager.ensureDatasetDirectory()

scaleWareHouse = True

def set_rendering_settings():
    '''
    Sets rendering settings for background
    '''
    bpy.context.scene.render.film_transparent = True
    # bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.resolution_percentage = 100
    cam_obj = bpy.data.objects['camera']

    bpy.context.scene.camera = cam_obj
    bpy.context.scene.cycles.samples = 400
    bpy.context.scene.frame_end = 1
    #bpy.context.scene.view_layers[0].cycles.use_denoising = True
    bpy.context.scene.cycles.use_denoising = True
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.02

    bpy.context.scene.view_settings.look = 'Medium Contrast'
    bpy.context.scene.render.image_settings.color_depth = '16'
    bpy.context.scene.cycles.max_bounces = 4
    bpy.context.scene.cycles.caustics_reflective = False
    bpy.context.scene.cycles.caustics_refractive = False
    bpy.context.scene.cycles.sample_clamp_indirect = 0
    bpy.context.scene.view_layers["View Layer"].use_pass_object_index = True
    bpy.context.scene.view_layers["View Layer"].use_pass_z = True
    bpy.context.scene.cycles.device = 'GPU'

def check_range(ranges, val):
    for ran in ranges:
        if val >= ran[0] and val <= ran[1]:
            return ran
    return 0

def get_sensor_size(sensor_fit, sensor_x, sensor_y):
    if sensor_fit == 'VERTICAL':
        return sensor_y
    return sensor_x

# BKE_camera_sensor_fit
def get_sensor_fit(sensor_fit, size_x, size_y):
    if sensor_fit == 'AUTO':
        if size_x >= size_y:
            return 'HORIZONTAL'
        else:
            return 'VERTICAL'
    return sensor_fit

def get_calibration_matrix_K_from_blender(camd):
    if camd.type != 'PERSP':
        raise ValueError('Non-perspective cameras not supported')
    scene = bpy.context.scene
    f_in_mm = camd.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size(camd.sensor_fit, camd.sensor_width, camd.sensor_height)
    sensor_fit = get_sensor_fit(
        camd.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camd.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camd.shift_y * view_fac_in_px / pixel_aspect_ratio
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((s_u, skew, u_0),
        (   0,  s_v, v_0),
        (   0,    0,   1)))
    return np.array(K)


def get_3x4_RT_matrix_from_blender(cam):
    # bcam stands for blender camera
    R_bcam2cv = Matrix(
        ((1, 0,  0),
        (0, -1, 0),
        (0, 0, -1)))

    # Transpose since the rotation is object rotation, 
    # and we want coordinate rotation
    # R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # T_world2bcam = -1*R_world2bcam * location
    #
    # Use matrix_world instead to account for all constraints
    location, rotation = cam.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    T_world2bcam = -1*R_world2bcam @ location
    # Use location from matrix_world to account for constraints:     
    #T_world2bcam = -1*R_world2bcam * location

    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv @ R_world2bcam
    T_world2cv = R_bcam2cv @ T_world2bcam

    # put into 3x4 matrix
    RT = Matrix((
        R_world2cv[0][:] + (T_world2cv[0],),
        R_world2cv[1][:] + (T_world2cv[1],),
        R_world2cv[2][:] + (T_world2cv[2],)
        ))
    return np.array(RT)


def get_3x4_P_matrix_from_blender(cam):
    K = get_calibration_matrix_K_from_blender(cam.data)
    RT = get_3x4_RT_matrix_from_blender(cam)
    return K @ RT

def getSpotLightPositionAndRotation(cam_x, cam_y, cam_z, cam_z_rot):
    height = 3
    if(cam_z_rot > np.pi):
        lightLocation = (cam_x, cam_y, cam_z+height)
        lightRotation = (0, -25.5/180 * np.pi, 0)
    else:
        lightLocation = (cam_x, cam_y, cam_z+height)
        lightRotation = (0, 25.5/180 * np.pi, 0)
    return lightLocation, lightRotation


def make_warehouse(no_rack_column, prob_of_box, corridor_width, num_rack_y, density_forklift, corridor_y, num_section_y, max_shelf_height, min_shelf_height, shelf_length_fix, shelf_height_fix):
   
    #This variable needs to be set to True if the script is being run from cli
    cli = False

    #Name = 'Dimi'

    bpy.ops.object.select_all(action='SELECT')
    #bpy.ops.object.delete(use_global=False, confirm=False)
    deleteSelectedObjects(bpy.context.selected_objects)
    print(sys.argv)

    ## For camera
    x_ranges_cam = [] #x coordinates where there are no racks
    y_ranges_cam_corr = []  # y coordinates of the corridor (new)
    y_ranges_cam_rack_inter = []    # y coordinates where we are looking at rackspace or intersection

    y_rack = 5.25
    #y_start = -(y_rack * (num_rack_y/2.0 - 1) + y_rack/2.0)
    #y_end = -y_start

    old_length_y = 94
    #new_length_y = y_end-y_start
    rack_lengths = []
    rack_heights = []
    for i in range(num_rack_y):
        # rack_lengths.append(random.uniform(5.25,10))
        # rack_heights.append(random.uniform(1.31,3.93))
        rack_lengths.append(shelf_length_fix)
        rack_heights.append(shelf_height_fix)
    # new_length_y = 5.25*(num_rack_y+2) + (num_rack_y/num_section_y)*corridor_y + y_rack
    new_length_y = sum(rack_lengths)  + (num_rack_y/num_section_y)*corridor_y + y_rack
    y_start = -((new_length_y/2)) + 10
    y_end = -y_start
    scale_y = new_length_y/old_length_y
    print(scale_y)


    reqd_len = no_rack_column*3*3 + (no_rack_column-1)*3*corridor_width + 3*corridor_width + 1.5*2*no_rack_column
    scale_x = reqd_len/31.5
    print(scale_x)

    # shelf_counts = [random.randrange(min_shelf_height,max_shelf_height+1) for i in range(num_rack_y//num_section_y + 2)]
    shelf_counts = [min_shelf_height, max_shelf_height] #list with two elements

    if(max(shelf_counts) <=3):
        scale_z = 1.0

    else:
        scale_z = 1.0 + ((max(shelf_counts)*3.9 - 2) * 0.1)
    #warehouse_length = 94*scale_x
    #warehouse_width = 31.5*scale_y
    warehouse_height = 8.9 * scale_z
    bpy.ops.import_scene.fbx( filepath = './objects/warehouses/warehouse_pillared/fully_closed.fbx' )
    #bpy.ops.wm.collada_import(filepath='./objects/warehouses/warehouse_pillared/warehouse_3.dae')

    #print("original dimensions")
    #print(bpy.data.objects['wall_window014'].dimensions)

    if(scaleWareHouse):
        bpy.ops.transform.resize(value=(scale_x,scale_y,scale_z))
        bpy.data.objects['columns001'].location = bpy.context.scene.cursor.location
        bpy.data.objects['columns001'].location.z -= 0.042904


    #print("new dimension")
    #print(bpy.data.objects['wall_window014'].dimensions)

    # create light datablock, set attributes
    #light_data = bpy.data.lights.new(name="light_2.80", type='POINT')
    #light_data.energy = 500
    #light_data.color = (1, 0.969472, 0.668894)
    #light_data.type = 'AREA'

    #for i in range(11):
    #    for j in range(3):
    #        print(i)
    #        # create new object with our light datablock
    #        light_object = bpy.data.objects.new(name="light"+str(i+1)+"_"+str(j+1), object_data=light_data)

    #        # link light object
    #        bpy.context.collection.objects.link(light_object)

    #        # make it active
    #        bpy.context.view_layer.objects.active = light_object

    #        #change location
    #        light_object.location = (-10+10*j, -37.1+7.65*i, 5.9)

    #def append_zero(num):
    #    return "." + str(num).zfill(3)


    # all_box_loc = './objects/primitives/boxes_avinash/'
    all_box_loc = '../synthetic_warehouse/objects/primitives/TextureCorrectedBoxes/'
    rack_loc = './objects/primitives/Racks/rack_modular2.dae'
    shelf_loc = '../synthetic_warehouse/objects/primitives/Racks/Shelf.dae'
    support_loc = '../synthetic_warehouse/objects/primitives/Racks/Support.dae'
    reference_line_up_loc = '../synthetic_warehouse/objects/primitives/blenderproc_objects/LineUp/LineUp.dae'
    reference_line_down_loc = '../synthetic_warehouse/objects/primitives/blenderproc_objects/LineDown/LineDown.dae'
    pallet_loc = './objects/primitives/pallet/pallet.dae'
    #fire_ext_loc = './objects/primitives/Extinguisher/fire1.dae'
    #forklift_loc = './objects/primitives/Forklift/final.obj'
    #CB_loc = './objects/primitives/ConveyerBelt/final.obj'
    #extinguisher_coords = [[10.5, 46.7, 2.5], [-10.5, 46.7, 2.5], [-10.5, -44.45, 2.5], [10.5, -44.45, 2.5]]
    #CB_coords = [[6.236, 1.849, 0], [6.405, 32.5, 0]]
    #forklift_coords = [[0, 10.78, 0], [0, 42.69, 0]]
    box_count = {"BoxA":0, "BoxB":0, "BoxC":0, "BoxD":0, "BoxF":0, "BoxG":0, "BoxH":0, "BoxI":0, "CrateA":0, "CrateB":0, "CrateC":0}

    #distance_between_racks_x = 1
    #distance_between_racks_y = 2.7


    z = -1.29

    x_coord = []
    y_coord = []
    mark_coord = []
    light_coord=[]
    fork_coord=[]


    #var = (no_rack_column-1)/2

    scaling = 12*scale_x

    section = 10*scale_x

    #def get_coord(factor):

    #    x_coord=[]

    for i in range(no_rack_column): # for racks
        for j in range(2):
            x_coord.append( (-scaling+(corridor_width*i)) + section*j)
            # x_coord.append( (-scaling+1.5+(corridor_width*i))+ section*j)

    for i in range(no_rack_column): # for line markers
        for j in range(2):
            mark_coord.append( (-scaling+(corridor_width*i)) -1 + section*j)
            mark_coord.append( (-scaling+(corridor_width*i)) +1 + section*j)
            # mark_coord.append( (-scaling+1.5+(corridor_width*i)) +1 + section*j)

    for i in range(no_rack_column): # for lights
        for j in range(2):
            light_coord.append( (-scaling+(corridor_width*i)) -2 + section*j)
            light_coord.append( (-scaling+(corridor_width*i)) +2 + section*j)

            # light_coord.append( (-scaling+1.5+(corridor_width*i)) +2 + section*j)

    for i in range(no_rack_column): # for forklifts
        for j in range(2):
            fork_coord.append( (-scaling+(corridor_width*i)) -1.5 + section*j)
            fork_coord.append( (-scaling+(corridor_width*i)) +1.5 + section*j)
            # fork_coord.append( (-scaling+1.5+(corridor_width*i)) +1.5 + section*j)


    #Now we get x coordinates of the camera from the mark coords
    #We use this for corridors and racks but not intersection areas
    # x_ranges_cam.append( (mark_coord[0]-2.5, mark_coord[0]) )
    mark_coord = sorted(mark_coord)
    for i in range(len(mark_coord)-1):
        if i%2 == 1: 
            #need to remove the pillar area from here
            x_ranges_cam.append((mark_coord[i],mark_coord[i+1])) #gap area 

    corridor_y += y_rack # to account for lost space due to length of rack
    y = y_start
    count_y=0
    left_track = y_start - y_rack/2
    print(rack_lengths)
    while y <= y_end and count_y<num_rack_y:
        # count_y += 1
        y_coord.append(y)
        # y += y_rack
        y+= rack_lengths[count_y]/2
        if y <= y_end and (count_y+1)<num_rack_y:
            y+= rack_lengths[count_y+1]/2
        count_y += 1
        if count_y % (num_rack_y//num_section_y) == 0:
            
            y_ranges_cam_rack_inter.append( (left_track, y - y_rack/2) )
            left_track =  y - y_rack/2 + corridor_y
            # y_ranges_cam_corr.append( (y + y_rack/2, left_track) )
            y += corridor_y 
    # print("THE COORDINATES ARE")
    # print(y_coord)
    # y_ranges_cam_rack_inter.append( (left_track, y_end - y_rack/2) )


    for i in range(len(y_ranges_cam_rack_inter) - 1):
        y_ranges_cam_corr.append( (y_ranges_cam_rack_inter[i][1], y_ranges_cam_rack_inter[i+1][0]) )

    #print(x_coord)
    #print(y_coord)

    subscript = 0
    #x_coord = x_start

    # def add_fire_ext(extinguisher_coords):
    #
    #     subscript = 0
    #     model = "fire_ext_10285_Fire_Extinguisher_v3_iterations-2"
    #
    #     for coords in extinguisher_coords:
    #
    #         for obj in bpy.data.objects:
    #             obj.tag = True
    #
    #         bpy.ops.import_scene.obj(filepath=fire_ext_loc)
    #
    #         for obj in bpy.data.objects:
    #             if obj.tag is False:
    #                 imported_object = obj
    #
    #         name = imported_object.name
    #
    #         bpy.data.objects[name].location.x += coords[0]
    #         bpy.data.objects[name].location.y += coords[1]
    #         bpy.data.objects[name].location.z += coords[2]
    #
    #         subscript += 1

    #fire_ext = Add_fire_ext(extinguisher_coords,fire_ext_loc,subscript)
    #fire_ext.add_fire_ext()

    #fork_lift = Add_forklift(forklift_coords,forklift_loc)
    #fork_lift.add_forklift()

    #CB = Add_CB(CB_coords,CB_loc)
    #CB.add_CB()

    racks_boxes = Place_racks_and_objects(subscript,prob_of_box,rack_loc,shelf_loc,support_loc,reference_line_up_loc,reference_line_down_loc,all_box_loc,box_count,x_coord,y_coord,z,num_section_y,corridor_y,shelf_counts,cli,rack_lengths,rack_heights,pallet_loc)
    racks_boxes.add_racks_boxes()

    for x in mark_coord:
        count = 0
        for y in y_coord:
            imported_object = bpy.ops.wm.collada_import(filepath='./objects/primitives/RackMarker/marker.dae')
            bpy.ops.transform.resize(value=(1,rack_lengths[count]/5.12,1))
            count+=1
            bpy.ops.transform.translate(value=(x, y, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

    for x in fork_coord:
        for y in y_coord:
            if  random.uniform(0,1) <= density_forklift:
                imported_object = bpy.ops.wm.collada_import(filepath='./objects/primitives/Forklift/final1.dae')
                bpy.ops.transform.translate(value=(x, y, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    #
    light_data = bpy.data.lights.new(name="light_2.80", type='POINT')
    light_data.energy = 2500
    # light_data.color = (1, 0.969472, 0.668894)
    light_data.color = (222/255, 188/255, 146/255)
    
    for i in light_coord:
        for j in y_coord:
            light_object = bpy.data.objects.new(name="light"+str(i+1)+"_"+str(j+1), object_data=light_data)
            # link light object
            bpy.context.collection.objects.link(light_object)
            # make it active
            bpy.context.view_layer.objects.active = light_object
            #change location
            light_object.location = (i, j, int(warehouse_height) - 10)

    #print(rack_heights)
#    ## update scene, if needed
#    #dg = bpy.context.evaluated_depsgraph_get()
#    #dg.upda
#    # bpy.ops.wm.save_as_mainfile(filepath='./tanvi.blend')
#    ##bpy.ops.export_scene.fbx(filepath='./rendered_warehouse/' +
#    ##gty

    #return 

    #camera placement
    focal_length = 22
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new('camera')
    cam = bpy.data.objects.new('camera', cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = focal_length 
    
    # Get the scene
    scene = bpy.data.scenes["Scene"]

    # Set render resolution
    scene.render.resolution_x = 480
    scene.render.resolution_y = 270
    scene.render.resolution_percentage = 100

    obj_in_fov = []
    
    for rack_number in range(len(assets.rack_to_shelf)):
        for im_num in range(3,4):
            distances = [[5, random.uniform(0.93,1.06)],
                         [random.uniform(6,7), random.uniform(1.8,2.29)], 
                         [random.uniform(8,10), 3.2],
                         [random.uniform(12,13), random.uniform(4.95, 5.35)]]
            bottom_shelf_coords = assets.get_shelf_location(assets.rack_to_shelf[rack_number][0])
            
            try:
                if rack_number < num_rack_y-1:
                    # distance_from_rack = 
                    cam_x = bottom_shelf_coords[0] + distances[im_num % len(distances)][0]
                    #valid_x = check_range(x_ranges_cam, cam_x)  
                    cam_z_rot = math.pi/2
                else:
                    cam_x = bottom_shelf_coords[0] - distances[im_num % len(distances)][0]
                    #valid_x = check_range(x_ranges_cam, cam_x)  
                    cam_z_rot = 3*math.pi/2

                cam_y = bottom_shelf_coords[1]
                cam_z = distances[im_num % len(distances)][1]
            except:
                continue 
            
            cam.location = mathutils.Vector((cam_x, cam_y, cam_z)) #3,4,5
            cam.rotation_euler = mathutils.Euler(( math.pi/2, 0.0, cam_z_rot ))       
            if(Constants.RENDERING_ON_ADA):
                bpy.context.scene.render.engine = 'CYCLES'  
                set_rendering_settings()
            result = bpycv.render_data() 
            objects = fov.get_objects_in_fov(rack_number)
            if objects[0] == "invalid":
                continue
            #log(str(rack_number) +str(objects))
            obj_in_fov.append(objects)
            assets.rack_cam_location.append(([cam_x, cam_y, cam_z, math.pi/2, 0.0, cam_z_rot]))
            #return
    # print(obj_in_fov)
    # return

    #deleting all the invisible objects
    bpy.ops.object.select_all(action='DESELECT')
    for line_obj in assets.invisible_lines_properties.keys():
        bpy.data.objects[line_obj].select_set(True) # Blender 2.8x
        bpy.ops.object.delete() 

    for im_num in range(len(obj_in_fov)):

        cam_x = assets.rack_cam_location[im_num][0]
        cam_y = assets.rack_cam_location[im_num][1]
        cam_z = assets.rack_cam_location[im_num][2]
        cam_z_rot = assets.rack_cam_location[im_num][5]

        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0.2
        cam.location = mathutils.Vector((cam_x, cam_y, cam_z)) #3,4,5
        cam.rotation_euler = mathutils.Euler(( math.pi/2, 0.0, cam_z_rot ))
        result = bpycv.render_data()
        cv2.imwrite(filePathManager.getAnuragAnnotationsImagePath(), result["image"][...,::-1])
        cameraProperties.image_size = (scene.render.resolution_x, scene.render.resolution_y)
        cameraProperties.update_camera(cam, scene)
        print("Written RGB and Annotations")
        generateAnnotations.generate_layout_annotations(
            obj_in_fov[im_num],
            filePathManager.getAnuragAnnotationsLabelPath(),
            shelf_height_fix,
            prob_of_box
        )
        if(Constants.GENERATE_KITTI):
            sceneCaptureNumber = filePathManager.getSceneCaptureNumber()
            writeKitti.writeKitti(result, sceneCaptureNumber, obj_in_fov[im_num])
            
        filePathManager.capturedScene()

        
prob_boxes = [0.2, 0.5, 1]
for i in range(1):
    # Configure your warehouse here


    # The warehouse is divided into 3 sections by the pillars.
    # Modelling after a real warehouse, racks are always kept in sets of 2


    # Use this variable to define how many sets of 2 racks you want in each section of the warehouse
    no_rack_column = 1

    # Use this variable to define the density of boxes on each rack [0,1]
    prob_of_box = 0.8#prob_boxes[i%3]

    # Use this variable to set the width of the corridor between 2 select_set
    corridor_width = random.uniform(13,14)

    #Use this variable to define the number of racks along the length of the warehouses
    num_rack_y = 6 #random.randint(6, 12)

    density_forklift = 0#random.uniform(0, 0.2)

    corridor_y = random.uniform(1,2)

    shelf_length_fix = 7#random.uniform(7,8)
    shelf_height_fix = random.uniform(2.5,3)
    
    num_section_y = 1#random.randint(2,4)
    # while num_rack_y % num_section_y == 1 or num_rack_y//num_section_y == 1:
    #     num_section_y = random.randint(7,8)

    #Use this variable to define the number of shelves in a rack unit
    max_shelf_height = 5#6
    min_shelf_height = 4
    make_warehouse(no_rack_column, prob_of_box, corridor_width, num_rack_y, \
            density_forklift, corridor_y, num_section_y, max_shelf_height, min_shelf_height, shelf_length_fix, shelf_height_fix)
    
    
    # make_warehouse(2,0,6,7,0,13,4,6,3)
    # make_warehouse(2,0,7,8,0,12,3,6,3)

# Get the velodyne from depth
#if(Constants.GENERATE_KITTI):
#    writeKitti.makeVelodynePoints(filePathManager.getSceneCaptureNumber())
#bpy.ops.wm.quit_blender()
