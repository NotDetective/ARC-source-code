from gpiozero import DistanceSensor

class Sonar:
    def __init__(self, echo=0, trigger=0):
        self.__distance_sensor = DistanceSensor(echo=echo, trigger=trigger)
        self.__is_active = False
        self.__trigger_distance = 100
        self.__is_triggerd = False
        
    def set_trigger_distance(self, distance):
        self.__trigger_distance = distance
    
    def get_trigger_distance(self):
        return self.__trigger_distance
    
    def set_active(self):
        self.__is_active = True
    
    def set_inactive(self):
        self.__is_active = False
        
    def is_active(self):
        return self.__is_active
    
    def reset_triggerd(self):
        self.__is_triggerd = False
    
    def is_triggerd(self):
        self.__is_triggerd = self.get_distance() <= self.get_trigger_distance()
        return self.__is_triggerd 
    
    def get_distance(self):
        if not self.__is_active:
            return 0
        return self.__distance_sensor.distance * 100
        