import threading
import time
from sonar.sonar import Sonar

class SonarController:
    
    def __init__(self):
        self.__sonars = {
            # "L": DistanceSensor(echo=14, trigger=15),
            # "R": DistanceSensor(echo=24, trigger=25),
            # "ML",
            # "MM",
            # "MR"
            "L": Sonar(echo=14, trigger=15),
            "R": Sonar(echo=24, trigger=25)
        }
        
        self.__running = False
        self.__thread = None
        
    def __update_loop(self, motor_controller):
        while self.__running:
            for name, sonar in self.__sonars.items():
                if sonar.is_active:
                    print(sonar.get_distance())
                    if sonar.is_triggerd():
                        motor_controller.stop_movement()
            
            time.sleep(0.05)
        
    def start_sonars(self, motor_controller):
        if not self.__running:
            self.__running = True
            self.__thread = threading.Thread(
                target=self.__update_loop, 
                args=(motor_controller, ),
                daemon=True
            )
            self.__thread.start()
            print("Sonar background thread started.")
    
    def stop_all(self):
        self.__running = False
        if self.__thread:
            self.__thread.join()
        print("Sonar thread stopped.")

    def reset_all(self):
        for sonar in self.__sonars.values():
            sonar.set_inactive()
            sonar.set_trigger_distance(100)
        
    def set_sonar_trigger_distance(self, sonar: str,  range_val: float):
        if sonar in self.__sonars:
            self.__sonars[sonar].set_trigger_distance(range_val)
    
    def set_sonar_active(self, sonar: str):
        if sonar in self.__sonars:
            self.__sonars[sonar].set_active()
    
    def set_sonar_inactive(self, sonar: str):
        if sonar in self.__sonars:
            self.__sonars[sonar].set_inactive()
    
    def set_sonars_trigger_distance(self, sonar_list: list[str], range_val: float):
        for name in sonar_list:
            if name in self.__sonars:
                self.__sonars[name].set_trigger_distance(range_val)
            
    def set_sonars_active(self, sonar_list: list[str]):
        for name in sonar_list:
            if name in self.__sonars:
                self.__sonars[name].set_active()

    def set_sonars_inactive(self, sonar_list: list[str]):
        for name in sonar_list:
            if name in self.__sonars:
                self.__sonars[name].set_inactive()
