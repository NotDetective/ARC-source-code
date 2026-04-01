from pathlib import Path
from ultralytics import YOLO

class Model:
    
    __FILENAME = "best.pt"
    
    def __init__(self, aProject, aName, yoloModel = "yolov8n.pt"):
        self.__model = None
        self.__project = aProject
        self.__name = aName
        self.__yoloModel = yoloModel
        
    def __get_train_path(self):
        return f"runs/detect/{self.__project}/{self.__name}/weights/{self.__FILENAME}"
    
    def check_for_trained_model(self):
        file = Path(self.__get_train_path())
        print(f"check for like at {self.__get_train_path()}")
        return file.is_file() 
    
    def get_trained_model(self):
        if self.check_for_trained_model():            
            if self.__model == None:
                self.__model = YOLO(self.__get_train_path())
            return self.__model
        return None
    