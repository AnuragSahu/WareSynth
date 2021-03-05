
import bpy
from bpy_extras.object_utils import world_to_camera_view

scene = bpy.context.scene

# needed to rescale 2d coordinates
render = scene.render
res_x = render.resolution_x
res_y = render.resolution_y

obj = bpy.data.objects['Cube']
cam = bpy.data.objects['Camera']

# use generator expressions () or list comprehensions []
verts = (vert.co for vert in obj.data.vertices)
coords_2d = [world_to_camera_view(scene, cam, coord) for coord in verts]

# 2d data printout:
rnd = lambda i: round(i)

print('x,y')
for x, y, distance_to_lens in coords_2d:
    print("{},{}".format(rnd(res_x*x), rnd(res_y*y)))