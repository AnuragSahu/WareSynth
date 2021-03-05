class CameraProperties(object):
    def __init__(self):
        self.camera_location = None
        self.camera_rotation = None
        self.camera_scale = None
        self.image_size = None
        self.intrinsic_matrix = None
        self.RT_matrix = None
        self.projection_matrix = None

    def update_camera(self, camera, scene):
        self.image_size = [
            scene.render.resolution_x,
            scene.render.resolution_y
        ]

        self.camera_location = [
            camera.location.x,
            camera.location.y,
            camera.location.z
        ]

        self.camera_rotation = [
            camera.rotation_euler.x, 
            camera.rotation_euler.z, 
            camera.rotation_euler.z
        ]

        self.camera_scale = [
            camera.scale.x, 
            camera.scale.y, 
            camera.scale.z
        ]

    def get_image_size(self):
        return self.image_size

    def get_camera_location(self):
        return self.camera_location

    def get_camera_rotation(self):
        return self.camera_rotation

    def get_camera_scale(self):
        return self.camera_scale

cameraProperties = CameraProperties()