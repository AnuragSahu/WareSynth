
class Assets(object):

    def __init__(self):
        self.rack_to_shelf = {}
        self.shelf_to_box = {}
        self.box_properties = {}
        self.shelf_properties = {}
        self.invisible_lines_properties = {}
        self.rack_cam_location = []
        self.light = []

    def reSetValues(self):
        self.rack_to_shelf = {}
        self.shelf_to_box = {}
        self.box_properties = {}
        self.shelf_properties = {}
        self.invisible_lines_properties = {}
        self.rack_cam_location = []

    def set_dict(self, rack_to_shelf, shelf_to_box, box_properties, shelf_properties, invisible_lines_properties):
        self.reSetValues()
        self.rack_to_shelf = rack_to_shelf
        self.shelf_to_box = shelf_to_box
        self.box_properties = box_properties
        self.shelf_properties = shelf_properties
        self.invisible_lines_properties = invisible_lines_properties

    def get_shelfs_in_rack(self, rack_number):
        return self.rack_to_shelf[rack_number]

    def get_boxes_from_shelfs(self, shelfs):
        box_names = []
        for i in shelfs:
            boxes = self.shelf_to_box[i]
            box_names.append([box for box in boxes])
        return box_names

    def get_boxes_in_rack(self, rack_number):
        shelfs = self.get_shelfs_in_rack(rack_number)
        box_names = self.get_boxes_from_shelfs(shelfs)
        return box_names

    def get_dict(self):
        return self.rack_to_shelf, self.shelf_to_box, self.box_properties

    def get_box_location(self, box):
        box_locations = self.box_properties[box][0]
        return box_locations

    def get_box_rotations(self, box):
        box_rotations_euler = self.box_properties[box][1]
        return box_rotations_euler

    def get_box_scale(self, box):
        box_scale = self.box_properties[box][2]
        return box_scale

    def get_box_dimensions(self, box):
        box_dimensions = self.box_properties[box][3]
        return box_dimensions

    def get_shelf_number_for_box(self, box):
        shelf_number = int(self.box_properties[box][4][0])
        return shelf_number

    def get_shelf_location(self, shelf):
        shelf_locations = self.shelf_properties[shelf][0]
        return shelf_locations

    def get_shelf_rotation(self, shelf):
        shelf_rotations_euler = self.shelf_properties[shelf][1]
        return shelf_rotations_euler

    def get_shelf_scale(self, shelf):
        shelf_scale = self.shelf_properties[shelf][2]
        return shelf_scale

    def get_shelf_dimensions(self, shelf):
        shelf_dimensions = self.shelf_properties[shelf][3]
        return shelf_dimensions

    def get_shelf_number(self, shelf):
        shelf_number = self.shelf_properties[shelf][4][0]
        return shelf_number


    

assets = Assets()