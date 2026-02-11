import os
from picamzero import Camera as PiCam

class MyCamera:
    def __init__(self):
        self.__cam = None
        self.folder = "images"
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def start_camera(self):
        cam = PiCam()
        cam.flip_camera(vflip=True, hflip=True)
        self.__cam = cam

    def take_foto(self, name):
        if self.__cam is None:
            print("Error: Camera not started!")
            return
            
        if not name.endswith(".jpg"):
            name += ".jpg" 
        
        path = os.path.join(self.folder, name)
        
        self.__cam.take_photo(path)
        print(f"Photo saved to: {path}")