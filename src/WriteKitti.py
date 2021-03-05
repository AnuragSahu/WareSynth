import numpy as np
import cv2
import GetCameraMatrices
import bpy
from FileNameManager import filePathManager

class WriteKitti(object):
    def __init__(self):
        self.K = None

    def get_dimensions(self, obj):
        lst = [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]
        dimensions = [str(lst[2]),str(lst[1]),str(lst[0])]
        return dimensions

    def build_string(self, types, truncated, occulded, alpha, bbox, dimensions, locations, rotation_y):
        empty_space = " "
        bbox_str = empty_space.join(bbox)
        loca_str = empty_space.join(locations)
        dim_str = empty_space.join(dimensions)
        lst = [str(types), str(truncated), str(occulded), str(alpha), bbox_str, dim_str, loca_str, str(rotation_y)]
        return empty_space.join(lst)

    def clamp(self, x, minimum, maximum):
        return max(minimum, min(x, maximum))

    def get_locations(self, obj, cam):
        RT = GetCameraMatrices.get_3x4_RT_matrix_from_blender(cam)
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

    def camera_view_bounds_2d(self, scene, cam_ob, me_ob):
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

        min_x = self.clamp(min(lx), 0.0, 1.0)
        max_x = self.clamp(max(lx), 0.0, 1.0)
        min_y = self.clamp(min(ly), 0.0, 1.0)
        max_y = self.clamp(max(ly), 0.0, 1.0)

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

    def writeKitti(self, result, count, objectsInFOV):
        depth_in_mm = result["depth"]
        np.save(
            filePathManager.kittiDepthPath + str(count).zfill(6)+".npy",
            depth_in_mm
        )
        cv2.imwrite(
            filePathManager.kittiImagePath + str(count).zfill(6) + ".png",
            result["image"][...,::-1]
        )

        camName = "camera"
        selectedObjects = [ bpy.context.scene.objects[objName] for objName in objectsInFOV]
        with open(filePathManager.kittiLabelPath + str(count).zfill(6) + ".txt",'w') as f:
            for obj in selectedObjects:
                types = obj.name.split(".")[0]
                if(types[:-1] == "Box"):
                    types = "Box"
                # writng the values for Kitti
                truncated = 0
                occulded = 0
                alpha = 0
                bbox = self.camera_view_bounds_2d(bpy.context.scene, bpy.context.scene.objects[camName], obj)
                dimensions = self.get_dimensions(obj)
                location = self.get_locations(obj, bpy.context.scene.objects[camName])
                rotation_y = np.pi/2-obj.rotation_euler.z #IDK
                to_write =  self.build_string(types, truncated, occulded,\
                                         alpha, bbox, dimensions, location,\
                                         rotation_y)
                f.write("%s\n" % to_write) 

        cam = bpy.data.objects[camName]
        P = GetCameraMatrices.get_3x4_P_matrix_from_blender(cam)
        self.K = GetCameraMatrices.get_calibration_matrix_K_from_blender(cam.data)

        str_2 = "P2: "

        for i in P:
            for j in i:
                str_2 = str_2 + str(j) + " "

        str_0 =  "P0: 0 0 0 0 0 0 0 0 0 0 0 0"
        str_1 =  "P1: 0 0 0 0 0 0 0 0 0 0 0 0"
        # str_2 =  "P2: 0 0 0 0 0 0 0 0 0 0 0 0"
        str_3 =  "P3: 0 0 0 0 0 0 0 0 0 0 0 0"
        str_R =  "R0_rect: 1 0 0 0 1 0 0 0 1"
        str_T = "Tr_velo_to_cam: 1 0 0 0 0 1 0 0 0 0 1 0"
        str_I = "Tr_imu_to_velo: 1 0 0 0 0 1 0 0 0 0 1 0"

        with open(filePathManager.kittiCalibpath +str(count).zfill(6)+".txt", 'w') as f:
            f.write("%s\n" % str_0)
            f.write("%s\n" % str_1)
            f.write("%s\n" % str_2)
            f.write("%s\n" % str_3)
            f.write("%s\n" % str_R)
            f.write("%s\n" % str_T)
            f.write("%s\n" % str_I)

    def makeVelodynePoints(self, totalScenes):
        K = self.K
        for ii in range(totalScenes):
            depth = np.load(filePathManager.kittiDepthPath + str(ii).zfill(6)+".npy")
            h,w = depth.shape
            camPoints = np.zeros((h*w, 4))
            i = 0
            for v in range(h):
                for u in range(w):
                    x = (u - K[0, 2]) * depth[v, u] / K[0, 0]
                    y = (v - K[1, 2]) * depth[v, u] / K[1, 1]
                    z = depth[v, u]
                    camPoints[i] =[x,y,z,1]
                    i += 1
            camPoints.astype('float32').tofile(filePathManager.kittiVelodynePath + str(ii).zfill(6)+".bin")

writeKitti = WriteKitti()