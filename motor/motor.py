from adafruit_motor import motor as adaMotor
from encoder.encoder import Encoder
from motor.motorMovement import MotorMovement

class Motor:
    
    __DEFAULT_MOTOR_RPM = 65
    
    def __init__(self, aPositavePin, aNegativePin, aForwardSpeed, aBackwardSpeed, aEncoder):
        self.__motor = adaMotor.DCMotor(aPositavePin, aNegativePin)
        self.__forwardSpeed = aForwardSpeed
        self.__backwardSpeed = aBackwardSpeed
        self.__rpm = self.__DEFAULT_MOTOR_RPM
        self.__encoder = aEncoder
        self.__current_throttle = 0.0
        self.__active_movement = None 

    def set_motor_movement(self, aMotorMovement: MotorMovement) -> None:
        self.__active_movement = aMotorMovement
        
    def run_motor(self, currentStep: int) -> None:
        if self.__active_movement is None:
            return
            
        movement_val = self.__active_movement.movement_value
        
        if currentStep <= 5:
            if movement_val >= 0.1:
                self.__current_throttle = self.__forwardSpeed
            elif movement_val <= -0.1:
                self.__current_throttle = self.__backwardSpeed
            else:
                self.__current_throttle = 0
                
            if currentStep == 5:
                self.__encoder.reset_count()
        
        else:
            target_rpm = self.get_motor_rpm()
            
            self.__current_throttle = self.__encoder.pi_controller(target_rpm, self.__current_throttle)

        self.__motor.throttle = self.__current_throttle
        
    def get_motor_rpm(self):
        val = self.__active_movement.movement_value
        if abs(val) < 0.1: return 0 
        return self.__rpm if val > 0 else -self.__rpm
    
    def reset_rpm(self):
        self.__rpm = self.__DEFAULT_MOTOR_RPM
        
    def set_motor_rpm(self, rpm):
        self.__rpm = rpm

    def reset_encoder(self):
        self.__encoder.reset_count()

    def stop(self):
        self.__current_throttle = 0
        self.__motor.throttle = 0
        self.__active_movement = None