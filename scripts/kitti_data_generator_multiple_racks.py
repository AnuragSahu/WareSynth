import bpy
import numpy as np
import math
import sys
from random import randrange
import random
from math import *
import mathutils
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import bpycv
import matplotlib.pyplot as plt
from math import *
from mathutils import Matrix,Vector
import os
import cv2

sys.path.append(os.path.relpath("../synthetic_warehouse/scripts/pillared_warehouse/"))

height_boxes = {
    "BoxA" : 0.424,
    "BoxB" : 0.3105,
    "BoxC" : 0.291,
    "BoxF" : 0.404,
    "BoxG" : 0.1255,
    "BoxH" : 0.172,
    "BoxI" : 0.585,
}

class Place_racks_and_objects():


    def __init__(self,subscript,prob_of_box,rack_loc,shelf_loc,support_loc,all_box_loc,z_positions,y_positions,box_count,offset_x,x_coord,y_coord,z,num_section_y,corridor_y,shelf_count):
        self.subscript = subscript
        self.rack_loc = rack_loc
        self.shelf_loc = shelf_loc
        self.support_loc = support_loc
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

    def place_box(self,model,x,y,z,rot_angle):
        if  random.uniform(0,1) <= self.prob_of_box:
            model_temp = model

            change = self.append_zero(self.box_count[model_temp])
            if self.box_count[model_temp] > 0:
                model = model + change
            else:
                model = model

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
            bpy.data.objects[model].location.x = x
            bpy.data.objects[model].location.y = y
            bpy.data.objects[model].location.z =z
            bpy.data.objects[model]["category_id"] = 1
            prev_model = model

    def place_racks_and_objects(self,rack_location,subscript,count,no_of_shelves):


        change = self.append_zero(subscript)
        bpy.ops.object.add(radius=1.0, type='EMPTY', enter_editmode=False, align='WORLD', location=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0])
        
        number = 0

        for i in range(no_of_shelves):
            shelf = "Shelf"
            support = "Support"
            change = self.append_zero(i)
            if i > 0:
                shelf = shelf + change
                support = support + change

            
            bpy.ops.wm.collada_import(filepath=self.shelf_loc)
            bpy.ops.wm.collada_import(filepath=self.support_loc)

            bpy.data.objects[shelf].location.z = 0.32 + 1.32 * i
            bpy.data.objects[support].location.z = 0.62 + 1.31 * i

        # Place the Boxes
        boxes = ["BoxA"]
        #boxes = ["BoxY"]
        prev_model=None
        thresh = 0.4
        for rows in range(no_of_shelves):

            len_rack = 5.04
            rack_start = -len_rack/2
            rack_end = len_rack/2
            model = random.choice(boxes)
            #dim_box = box_dims["model"]
            box_x = 0.962#dim_box[0]
            box_y = 0.744#dim_box[1]
            rot_angle = random.uniform(-20,20)
            
            curr_boxy = 0
            curr_protrusion = 0

            next_protrusion = abs((rot_angle/90))* (box_x/2-box_y/2)
            next_boxy =  box_y/2

            yloc_curr = rack_start
            yloc_next = yloc_curr + curr_boxy + curr_protrusion + thresh + next_boxy/2 + next_protrusion
            
            while(yloc_next<= (rack_end-thresh)):

                curr_boxy = next_boxy
                curr_protrusion = next_protrusion
                yloc_curr = yloc_next
                self.place_box(model,self.offset_x+ rack_location[0],yloc_curr + rack_location[1], rows*1.29 + 0.35,rot_angle)

                model = random.choice(boxes)
                #dim_box = box_dims["model"]
                box_x = 0.962#dim_box[0]
                box_y = 0.744#dim_box[1]

                rot_angle = random.uniform(-20,20)

                next_protrusion = abs((rot_angle/90))* (box_x/2-box_y/2)
                next_boxy =  box_y/2
                yloc_next = yloc_curr + curr_boxy + curr_protrusion + thresh + next_boxy/2 + next_protrusion
                

    def add_racks_boxes(self,no_of_shelves):
        for i in range(1):
            count=0
            for j in range(1):
                count+=1
                model = "Rack Model"
                change = self.append_zero(self.subscript)
                if self.subscript > 0:
                    name = model + change
                else:
                    name = model

                self.place_racks_and_objects([0, 0, self.z], self.subscript,count,no_of_shelves)

                self.subscript += 1

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def camera_view_bounds_2d(scene, cam_ob, me_ob):
    """
    Returns camera space bounding box of mesh object.

    Negative 'z' value means the point is behind the camera.

    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.

    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg me: Untransformed Mesh.
    :type me: :class:`bpy.types.Mesh´
    :return: a Box object (call its to_tuple() method to get x, y, width and height)
    :rtype: :class:`Box`
    """

    mat = cam_ob.matrix_world.normalized().inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_eval = me_ob.evaluated_get(depsgraph)
    me = mesh_eval.to_mesh()
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z

        if camera_persp:
            if z == 0.0:
                lx.append(0.5)
                ly.append(0.5)
            else:
                frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)

    mesh_eval.to_mesh_clear()

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac

    bbox =  [
        round(min_x * dim_x),            # X
        round(dim_y - max_y * dim_y),    # Y
        round((max_x - min_x) * dim_x),  # Width
        round((max_y - min_y) * dim_y)   # Height
    ]

    bbox = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]
    temp = [str(i) for i in bbox]
    return temp

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

def get_locations(obj, cam):
    RT = get_3x4_RT_matrix_from_blender(cam)
    extra_vec = np.array([0,0,0,1])
    RT = np.vstack((RT, extra_vec))
    locations = np.array([
        obj.location[0],
        obj.location[1],
        obj.location[2],
        1
    ])

    locations = RT @ locations
    locations /= locations[3]
    locations = locations[:3]
    locations = [locations[0],locations[1]+obj.dimensions.z/2,locations[2]]
    locations = [str(i) for i in locations]
    return locations

def get_3x4_P_matrix_from_blender(cam):
    K = get_calibration_matrix_K_from_blender(cam.data)
    RT = get_3x4_RT_matrix_from_blender(cam)
    return K @ RT

def write_k_mat(k_mat,K):
    k_mat.write("[")
    for i in K:
        k_mat.write("[")
        for j in i:
            k_mat.write(str(j)+str(" "))
        k_mat.write("],")
    k_mat.write("]")

def build_string(types, truncated, occulded, alpha, bbox, dimensions, locations, rotation_y):
    empty_space = " "
    bbox_str = empty_space.join(bbox)
    loca_str = empty_space.join(locations)
    dim_str = empty_space.join(dimensions)
    lst = [str(types), str(truncated), str(occulded), str(alpha), bbox_str, dim_str, loca_str, str(rotation_y)]
    return empty_space.join(lst)

def get_dimensions(obj):
    lst = [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]
    dimensions = [str(lst[2]),str(lst[1]),str(lst[0])]
    return dimensions

no_of_warehouses = 1 # The number of warehouse you want
no_of_scenes =1 # The number of scenes you want in each warehouse
no_of_shelves = 1 # The number of shelves on the rack
prob_list = [0.5,0.6,0.7,0.8]
#camera_pos = [[-9.37191, 0.130869,3.48572],[-0.404, 8.998, 5.216],[-6.62155, -5.63537,4.93942],[-6.24607, 5.948, 5.060]]
#camera_rot = [[69.6,0,-90.8],[62,0,-178],[60.4,0,-49.6],[59.6,0,-134]]
camera_rot = [90,0,-90]
corridor_y = 1
num_section_y = 1
all_box_loc = '../synthetic_warehouse/objects/primitives/blenderproc_objects/'
rack_loc = '../synthetic_warehouse/objects/primitives/Racks/rack_modular3.dae'
shelf_loc = '../synthetic_warehouse/objects/primitives/Racks/Shelf.dae'
support_loc = '../synthetic_warehouse/objects/primitives/Racks/Support.dae'


offset_x = -0
z_positions = []
y_positions = [-1, 1]

try:
    os.mkdir("./training")
except FileExistsError:
    print("Parent directory already exists")


path_img = "./training/image_2/"
path_depth = "./training/depth/"
path_calib = "./training/calib/"
path_label = "./training/label_2/"
try:
    os.mkdir(path_img)
except FileExistsError:
    print("Path already exists")
    
try:
    os.mkdir(path_depth)
except FileExistsError:
    print("Path already exists")

try:
    os.mkdir(path_calib)
except FileExistsError:
    print("Path already exists")

try:
    os.mkdir(path_label)
except FileExistsError:
    print("Path already exists")
count=-1
for wno in range(no_of_warehouses):
    Name = 'Dimi'

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    #print(sys.argv)
    
    light_data = bpy.data.lights.new(name="light_2.80", type='POINT')
    light_data.energy = 500

    # create new object with our light datablock
    light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)

    # link light object
    bpy.context.collection.objects.link(light_object)

    # make it active 
    bpy.context.view_layer.objects.active = light_object

    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new('camera')
    cam = bpy.data.objects.new('camera', cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.data.lens = 50

#    prob_of_box = random.choice(prob_list)
    prob_of_box = 1

    box_count = {"BoxA":0, "BoxB":0, "BoxC":0, "BoxD":0, "BoxF":0, "BoxG":0, "BoxH":0, "BoxI":0, "BoxY":0}


    #z = -1.29
    z = 0

    x_coord = []
    y_coord = []

    height_boxes = {
        "BoxA" : 0.424,
        "BoxB" : 0.3105,
        "BoxC" : 0.291,
        "BoxF" : 0.404,
        "BoxG" : 0.1255,
        "BoxH" : 0.172,
        "BoxI" : 0.585,
    }

    subscript = 0

    racks_boxes = Place_racks_and_objects(subscript,
                                        prob_of_box,
                                        rack_loc,
                                        shelf_loc,
                                        support_loc,
                                        all_box_loc,
                                        z_positions,
                                        y_positions,
                                        box_count,
                                        offset_x,
                                        x_coord,
                                        y_coord,
                                        z,
                                        num_section_y,
                                        corridor_y,1)
    racks_boxes.add_racks_boxes(no_of_shelves)

#    for sno in range(no_of_scenes):
#        count+=1
#        camera_pos = [random.uniform(-10,-8),random.uniform(-1.5,1.5),random.uniform(-0.5,1.5*no_of_shelves)]
#        light_object.location = (camera_pos[0]+4, camera_pos[1], camera_pos[2]+2)
#        cam.location = mathutils.Vector((camera_pos[0], camera_pos[1], camera_pos[2]))
#        cam.rotation_euler = mathutils.Euler( (camera_rot[0]*math.pi/180, camera_rot[1]*math.pi/180, camera_rot[2]*math.pi/180))
#        
#        k_mat = open('./k_mat.txt','w+')
#        K = get_calibration_matrix_K_from_blender(cam.data)
#        write_k_mat(k_mat,K)
#        result = bpycv.render_data()

#        cv2.imwrite(path_img+str(count).zfill(6)+".png", result["image"][...,::-1])

#        depth_in_mm = result["depth"]
#        np.save(path_depth+str(count).zfill(6) +".npy", depth_in_mm)

#        cam_name = "camera"

#        sel_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
#        with open(path_label +str(count).zfill(6)+".txt", 'w') as f:
#            for obj in sel_objs:
#                types = obj.name.split(".")[0][:-1]
#                if types != "shel":
#                    truncated = 0 # Dontcare
#                    occulded = 0  # Dontcare
#                    alpha = 0     # Dontcare
#                    bbox = camera_view_bounds_2d(bpy.context.scene, bpy.context.scene.objects[cam_name], obj)
#                    dimensions = get_dimensions(obj)
#                    location = get_locations(obj, bpy.context.scene.objects[cam_name])
#                    rotation_y = np.pi/2-obj.rotation_euler.z #IDK
#                    to_write =  build_string(types, truncated, occulded, alpha, bbox, dimensions, location, rotation_y)
#                    # f.write(to_write)
#                    f.write("%s\n" % to_write)

#        
#        cam = bpy.data.objects[cam_name]
#        P = get_3x4_P_matrix_from_blender(cam)

#        str_2 = "P2: "

#        for i in P:
#            for j in i:
#                str_2 = str_2 + str(j) + " "

#        str_0 =  "P0: 0 0 0 0 0 0 0 0 0 0 0 0"
#        str_1 =  "P1: 0 0 0 0 0 0 0 0 0 0 0 0"
#        # str_2 =  "P2: 0 0 0 0 0 0 0 0 0 0 0 0"
#        str_3 =  "P3: 0 0 0 0 0 0 0 0 0 0 0 0"
#        str_R =  "R0_rect: 1 0 0 0 1 0 0 0 1"
#        str_T = "Tr_velo_to_cam: 1 0 0 0 0 1 0 0 0 0 1 0"
#        str_I = "Tr_imu_to_velo: 1 0 0 0 0 1 0 0 0 0 1 0"

#        with open(path_calib +str(count).zfill(6)+".txt", 'w') as f:
#            f.write("%s\n" % str_0)
#            f.write("%s\n" % str_1)
#            f.write("%s\n" % str_2)
#            f.write("%s\n" % str_3)
#            f.write("%s\n" % str_R)
#            f.write("%s\n" % str_T)
#            f.write("%s\n" % str_I)
#            
#K = np.array([[2666.666748046875, 0.0, 960.0 ],[0.0, 2666.666748046875, 540.0 ],[0.0, 0.0, 1.0 ],])
#for ii in range(no_of_warehouses*no_of_scenes):
#        path = "./training/velodyne/"
#        try:
#            os.mkdir(path)
#        except FileExistsError:
#            print("Path already exists")
#        
#        depth = np.load("./training/depth/"+str(ii).zfill(6)+".npy")
#        h,w = depth.shape
#        cam_points = np.zeros((h * w, 4))

#        i = 0
#        for v in range(h):
#            for u in range(w):

#                x = (u - K[0, 2]) * depth[v, u] / K[0, 0]
#                y = (v - K[1, 2]) * depth[v, u] / K[1, 1]
#                z = depth[v, u]
#                cam_points[i] =[x,y,z,1]

#                i += 1
#        cam_points.astype('float32').tofile(path+"/"+str(ii).zfill(6)+".bin")

#print("DONE")
