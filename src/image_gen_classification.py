

def pad_range(ip_range, part_to_remove):
    op_range = []
    for i in range(len(ip_range)):
        lb = ip_range[i][0]
        ub = ip_range[i][1]
        lb += part_to_remove / 2 
        ub -= part_to_remove / 2
        if lb > ub:
            print("CANNOT PAD THE RANGE") 
            lol = pad_range([(ip_range[i][0],ip_range[i][1])], part_to_remove/2)[0]
            op_range.append((lol[0], lol[1]))
        else:
            op_range.append((lb,ub))
    print(op_range)
    return op_range

def check_range(ranges, val):
    for ran in ranges:
        if val >= ran[0] and val <= ran[1]:
            # if ran[1] - val > val - ran[0]: #closer to the right
            #     return -1
            # else:   #closer to the left
            #     return 1
            return ran
    return 0

def get_label(x, y, z_angle, x_ranges_cam, y_ranges_cam_corr, y_ranges_cam_rack_inter, y_ranges_cam_rack_inter_padded, y_ranges_cam_rack_inter_inc):
    offset = 90
    #corridor area
    if check_range(y_ranges_cam_corr, y) != 0:
        if z_angle == 90 or z_angle==270:
            return "corridor"
        elif check_range(y_ranges_cam_rack_inter_inc, y)!=0:
            val = check_range(y_ranges_cam_rack_inter_inc, y) 
            if val < 0 and check_range([[180-offset, 180+offset]], z_angle)!=0: #facing outside left
                return "intersection"
            elif val > 0 and check_range([[360-offset, 360], [0, 0+offset]], z_angle)!=0: #facing outside right
                return "intersection"
            else:
                return "rackspace"
        else:
            return "intersection"
    #camera is inside a rack: error
    elif check_range(x_ranges_cam, x) == 0:
        return "invalid location"


    #rackspace vs intersection
    if check_range(y_ranges_cam_rack_inter_padded, y) != 0:
        return "rackspace"
    else:
        val = check_range(y_ranges_cam_rack_inter, y) 
        if val < 0 and check_range([[180-offset, 180+offset]], z_angle)!=0: #facing outside left
            return "intersection"
        elif val > 0 and check_range([[360-offset, 360], [0, 0+offset]], z_angle)!=0: #facing outside right
            return "intersection"
        else:
            return "rackspace"
    
    
#camera outputs
uid = "%d_%d_%d_%d_%d_%d_%d_%d_%d"%(no_rack_column, prob_of_box, corridor_width, num_rack_y, density_forklift, corridor_y, num_section_y, max_shelf_height, min_shelf_height)
focal_length = 24
camera_height = 1.5
scene = bpy.context.scene
cam_data = bpy.data.cameras.new('camera')
cam = bpy.data.objects.new('camera', cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = focal_length 

y_ranges_cam_rack_inter_padded = pad_range(y_ranges_cam_rack_inter, y_rack*7/4)
y_ranges_cam_rack_inter_inc = pad_range(y_ranges_cam_rack_inter, -(corridor_width + 1))

#defining the cam positions
cam_positions = []

#y_start and y_end are reused
for i in range(len(x_ranges_cam)):
    x = (x_ranges_cam[i][0] + x_ranges_cam[i][1])/2
    cam_positions.append( ((x, y_start, 180),(x, y_end, 180)) )
print(len(cam_positions))

x_start = x_ranges_cam[0][0]
x_end = x_ranges_cam[len(x_ranges_cam)-1][1]
for i in range(len(y_ranges_cam_corr)):
    y = (y_ranges_cam_corr[i][0]+y_ranges_cam_corr[i][1])/2
    cam_positions.append( ((x_start, y, 90),(x_end, y, 90)) )
print(len(cam_positions))

# for i in range(len(x_ranges_cam)-1):
#     x_start = (x_ranges_cam[i][0] + x_ranges_cam[i][1])/2
#     x_end = (x_ranges_cam[i][1] + x_ranges_cam[i+1][0])/2
#     y_start = y_ranges_cam_rack_inter[1][1] #need to check the angles
#     y_end = (y_ranges_cam_corr[1][0] + y_ranges_cam_corr[1][1])/2 
#     #cam_positions.append( ((x_start, y_start, 180),(x_end, y_end, 90)) )
# print(len(cam_positions))


for j in range(len(cam_positions)):

    # if random.uniform(0,1) < 0.8:
    #     continue
    x_start = cam_positions[j][0][0]
    x_end = cam_positions[j][1][0]
    y_start = cam_positions[j][0][1]
    y_end = cam_positions[j][1][1]
    z_angle_start = cam_positions[j][0][2]
    z_angle_end = cam_positions[j][1][2]
    if x_start != x_end:
        num_steps = abs(x_end - x_start) // 2.625 
    elif y_start != y_end:
        num_steps = abs(y_end - y_start) // 2.625
    else:
        num_steps = 5
    num_steps += 1
    num_steps = floor(num_steps)

    #clockwise vs anticlockwise rotation
    if z_angle_start < z_angle_end:
        dirn = +1
    else:
        dirn = -1 

    outfile = open("images_data/labels.txt", "a")
    for i in range(num_steps):
        x = float(x_start) + float((x_end - x_start)//num_steps * i) 
        y = float(y_start) + float((y_end - y_start)//num_steps * i) 
        z_angle = float(z_angle_start) + float(dirn*(z_angle_end - z_angle_start)//num_steps * i)

        imname = uid+"__%d_%d_%d_%d_%d"%(focal_length,camera_height, x,y,z_angle)
        outfile.write(imname + " "+ get_label(x, y, z_angle, x_ranges_cam, y_ranges_cam_corr, y_ranges_cam_rack_inter, \
            y_ranges_cam_rack_inter_padded, y_ranges_cam_rack_inter_inc) +"\n") 
        cam.location = mathutils.Vector((x, y, camera_height))
        cam.rotation_euler = mathutils.Euler(( math.pi/2, 0.0, (z_angle*math.pi)/180 ))
        # scene.render.image_settings.file_format = 'PNG'
        # scene.render.filepath = "images_data/"+str(imname)+".png"
        # bpy.context.scene.render.engine = 'CYCLES' 
        # bpy.ops.render.render(write_still = 1)
        path_img = "images_data/"+str(imname)+".png"
        result = bpycv.render_data()
        cv2.imwrite(path_img, result["image"][...,::-1])
    
    outfile.close()

    time.sleep(30)

