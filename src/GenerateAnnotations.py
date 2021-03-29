from FOV import fov
from Console import log
from Assets import assets
from FileNameManager import filePathManager
from CameraProperties import cameraProperties

class GenerateAnnotations(object):
    def __init__(self):
        self.comma = ", "
        self.space = " "
        self.layout_annotations = ""
        self.KITTI_annotations = ""

    def elements_as_string(self, lst):
        str_lst = [str(i) for i in lst]
        return str_lst

    def generate_layout_annotations(self, objects, file_name, intershelfDistance, prob_boxes):
        # objects = fov.get_objects_in_fov(rack_number)
        # log("Rack in Focous : "+str(rack_number))
        camera_location = cameraProperties.get_camera_location()
        camera_rotation = cameraProperties.get_camera_rotation()
        camera_scale = cameraProperties.get_camera_scale()
        for object in objects:
            if(object[:3] != "She"):
                object_type = "Box"
                object_shelf_number = assets.get_shelf_number_for_box(object)
                object_location = assets.get_box_location(object)
                object_rotations = assets.get_box_rotations(object)
                object_dimensions = assets.get_box_dimensions(object)
                object_scale = assets.get_box_scale(object)
                inter_shelf_distance = intershelfDistance
                
            elif(object[:3] == "She"):
                object_type = "Shelf"
                object_shelf_number = assets.get_shelf_number(object)
                object_location = assets.get_shelf_location(object)
                object_rotations = assets.get_shelf_rotation(object)
                object_dimensions = assets.get_shelf_dimensions(object)
                object_scale = assets.get_shelf_scale(object)
                inter_shelf_distance = intershelfDistance
        
            self.update_layout_annotations([
                str(object_type),
                str(object_shelf_number),
                self.comma.join(self.elements_as_string(object_location)),
                self.comma.join(self.elements_as_string(object_rotations)),
                self.comma.join(self.elements_as_string(object_dimensions)),
                self.comma.join(self.elements_as_string(object_scale)),
                self.comma.join(self.elements_as_string(camera_location)),
                self.comma.join(self.elements_as_string(camera_rotation)),
                self.comma.join(self.elements_as_string(camera_scale)),
                str(inter_shelf_distance),
                str(prob_boxes)
            ])
        self.write_layout_annotations(file_name)

    def update_layout_annotations(self, objects_and_camera):
        # log("before : ")
        # log(self.layout_annotations)
        # log("after : ")
        # log(self.comma.join(objects_and_camera)+"\n")
        self.layout_annotations =  self.layout_annotations  + self.comma.join(objects_and_camera)+"\n"

    def write_layout_annotations(self, file_name):
        f = open(file_name, "w")
        f.write(self.layout_annotations)
        f.close()
        self.layout_annotations = ""

    def generate_kitti_annotations(self, rack_number, file_name):
        objects = fov.get_objects_in_fov(rack_number)
        camera_location = cameraProperties.get_camera_location()
        camera_rotation = cameraProperties.get_camera_rotation()
        camera_scale = cameraProperties.get_camera_scale()
        for object in objects:
            if(object[:3] == "Box"):
                object_type = "Box"
                object_location = assets.get_box_location(object)
                object_rotations = assets.get_box_rotations(object)
                object_dimensions = assets.get_box_dimensions(object)
                object_scale = assets.get_box_scale(object)
                
            elif(object[:3] == "She"):
                object_type = "Shelf"
                object_location = assets.get_shelf_location(object)
                object_rotations = assets.get_shelf_rotation(object)
                object_dimensions = assets.get_shelf_dimensions(object)
                object_scale = assets.get_shelf_scale(object)
        
            #PROCESS THE VALUES TO BE IN KITTI

            self.update_KITTI_annotations([
                object_type,
                self.comma.join(object_location),
                self.comma.join(object_rotations),
                self.comma.join(object_dimensions),
                self.comma.join(object_scale),
                self.comma.join(camera_location),
                self.comma.join(camera_rotation),
                self.comma.join(camera_scale),
            ])
        self.write_KITTI_annotations(file_name)
    
    def update_KITTI_annotations(self, annotations):
        self.KITTI_annotations = self.space.join(annotations)+"\n"
        

    def write_KITTI_annotations(self, file_name):
        f = open(file_name, "w")
        f.write(self.KITTI_annotations)
        f.close()
        self.KITTI_annotations = None

generateAnnotations = GenerateAnnotations()