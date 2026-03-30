import os
import numpy as np
from picamzero import Camera as PiCam


class MyCamera:
    def __init__(self):
        self.__cam = None
        self.folder = "images"
        self.__FOV = 120

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def get_FOV(self):
        return self.__FOV

    def start_camera(self):
        self.__cam = PiCam()
        # Ensure correct orientation
        self.__cam.flip_camera(vflip=True, hflip=True)

    def get_cam(self):
        return self.__cam

    def get_frame(self):
        """Returns the frame as an RGB numpy array."""
        if self.__cam is None:
            return None
        return np.array(self.__cam.capture_array())

    def stop_camera(self):
        if self.__cam:
            self.__cam.stop_preview()