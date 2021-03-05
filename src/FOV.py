from bpy import context
import bpy
from mathutils import Matrix,Vector
from mathutils.geometry import normal
from Assets import assets
from CameraProperties import cameraProperties
import numpy as np
from bpy_extras.object_utils import world_to_camera_view


class FOV(object):

    def camera_as_planes(self, scene, obj):
        """
        Return planes in world-space which represent the camera view bounds.
        """

        camera = obj.data
        # normalize to ignore camera scale
        matrix = obj.matrix_world.normalized()
        frame = [matrix @ v for v in camera.view_frame(scene=scene)]
        origin = matrix.to_translation()

        planes = []
        is_persp = (camera.type != 'ORTHO')
        for i in range(4):
            # find the 3rd point to define the planes direction
            if is_persp:
                frame_other = origin
            else:
                frame_other = frame[i] + matrix.col[2].xyz

            n = normal(frame_other, frame[i - 1], frame[i])
            d = -n.dot(frame_other)
            planes.append((n, d))

        if not is_persp:
            # add a 5th plane to ignore objects behind the view
            n = normal(frame[0], frame[1], frame[2])
            d = -n.dot(origin)
            planes.append((n, d))

        return planes


    def side_of_plane(self, p, v):
        return p[0].dot(v) + p[1]


    def is_segment_in_planes(self, p1, p2, planes):
        dp = p2 - p1

        p1_fac = 0.0
        p2_fac = 1.0

        for p in planes:
            div = dp.dot(p[0])
            if div != 0.0:
                t = -self.side_of_plane(p, p1)
                if div > 0.0:
                    # clip p1 lower bounds
                    if t >= div:
                        return False
                    if t > 0.0:
                        fac = (t / div)
                        p1_fac = max(fac, p1_fac)
                        if p1_fac > p2_fac:
                            return False
                elif div < 0.0:
                    # clip p2 upper bounds
                    if t > 0.0:
                        return False
                    if t > div:
                        fac = (t / div)
                        p2_fac = min(fac, p2_fac)
                        if p1_fac > p2_fac:
                            return False

        ## If we want the points
        # p1_clip = p1.lerp(p2, p1_fac)
        # p2_clip = p1.lerp(p2, p2_fac)        
        return True


    def point_in_object(self, obj, pt):
        xs = [v[0] for v in obj.bound_box]
        ys = [v[1] for v in obj.bound_box]
        zs = [v[2] for v in obj.bound_box]
        pt = obj.matrix_world.inverted() @ pt
        return (min(xs) <= pt.x <= max(xs) and
                min(ys) <= pt.y <= max(ys) and
                min(zs) <= pt.z <= max(zs))


    def object_in_planes(self, obj, planes):
        
        matrix = obj.matrix_world
        box = [matrix @ Vector(v) for v in obj.bound_box]
        for v in box:
            if all(self.side_of_plane(p, v) > 0.0 for p in planes):
                # one point was in all planes
                return True

        # possible one of our edges intersects
        edges = ((0, 1), (0, 3), (0, 4), (1, 2),
                (1, 5), (2, 3), (2, 6), (3, 7),
                (4, 5), (4, 7), (5, 6), (6, 7))
        if all(self.is_segment_in_planes(box[e[0]], box[e[1]], planes)
            for e in edges):
            return False

        return False


    def objects_in_planes(self, objects, planes, origin):
        """
        Return all objects which are inside (even partially) all planes.
        """
        return [obj for obj in objects
                if self.point_in_object(obj, origin) or
                self.object_in_planes(obj, planes)]

    def select_objects_in_camera(self):
        scene = context.scene
        origin = scene.camera.matrix_world.to_translation()
        planes = self.camera_as_planes(scene, scene.camera)
        objects_in_view = self.objects_in_planes(scene.objects, planes, origin)

        objects_in_fov = []

        for obj in objects_in_view:
            objects_in_fov.append(obj.name)
        
        return objects_in_fov


    def get_objects_in_fov(self, rack_in_focous):
        possible_obj_in_fov = self.select_objects_in_camera()
        # print("beofre",obj_in_fov)
        shelfs = assets.get_shelfs_in_rack(rack_in_focous)

        objects_in_FOV = []

        shelfs_count = 0

        for shelf in shelfs:

            lineup = "LineUp"
            linedown = "LineDown"
            
            if shelf == "Shelf":
                pass
            else:
                lineup +=shelf[-4:]
                linedown +=shelf[-4:]

            if shelf in possible_obj_in_fov:
                shelfs_count += 1

                if lineup in possible_obj_in_fov and linedown in possible_obj_in_fov:

                    objects_in_FOV.append(shelf)

                    boxes = assets.shelf_to_box[shelf]
                
                    for box in boxes:
                        if box in possible_obj_in_fov:
                            objects_in_FOV.append(box)
                
                elif linedown not in possible_obj_in_fov and lineup not in possible_obj_in_fov:
                    continue

                else:
                    return ["invalid"]

        # print(objects_in_FOV)

        if shelfs_count < 2:
            return ["invalid"]
            
        return objects_in_FOV

fov = FOV()