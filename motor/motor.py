from adafruit_motor import motor as aMotor

class Motor:
    def __init__(self, motor, isInInverted = False):
        self.__motor = motor
        self.__isInInverted = isInInverted
    
    
    def get_motor(self):
        return self.__motor
    
    def set_speed(self, speed):           
        if speed is None:
            self.__motor.throttle = None
        elif -1.0 <= speed <= 1.0 :
            self.__motor.throttle = self.__handle_speed(speed)
        else:
            raise ValueError(f"Speed must be between -1.0 and 1.0. Received: {speed}")
        
    def __handle_speed(self, speed):        
        
        if self.__isInInverted:
            return speed * -1
        else:
            return speed
         