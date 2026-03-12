from adafruit_motor import motor as adaMotor

from encoder.encoder import Encoder
from motor.motorMovement import MotorMovement

# class Motor:
#     def __init__(self, aPositavePin: int, aNegativePin: int, aForwardSpeed: float, aBackwardSpeed: float, aEncoder: Encoder) -> None:
#         self.__motor = adaMotor.DCMotor(aPositavePin, aNegativePin)
#         self.__forwardSpeed = aForwardSpeed
#         self.__backwardSpeed = aBackwardSpeed
#         self.__encoder = aEncoder
        
        
#     def set_motor_movement(self, aMoterMovement: MotorMovement) -> None:
#         movement = aMoterMovement.movement_value
        
#         if movement is None or movement == 0:
#             self.__motor.throttle = 0
#             return

#         # Determine target RPM based on direction
#         if movement >= 0.1:
#             target_rpm = 65
#             current_speed = self.__forwardSpeed
#         else:
#             target_rpm = -65
#             current_speed = self.__backwardSpeed
        
#         # Update throttle using the PI controller
#         # Note: You need a way to track the 'current_speed' over time 
#         # for the PI adjustment to actually accumulate!
#         new_throttle = self.__encoder.pi_controller(target_rpm, current_speed)
#         self.__motor.throttle = new_throttle
        
#     def stop(self) -> None:
#         self.__motor.throttle = MotorMovement.LOCKED.movement_value
         
class Motor:
    def __init__(self, aPositavePin, aNegativePin, aForwardSpeed, aBackwardSpeed, aEncoder):
        self.__motor = adaMotor.DCMotor(aPositavePin, aNegativePin)
        self.__encoder = aEncoder
        self.__current_throttle = 0.0 
        
    def set_motor_movement(self, aMoterMovement: MotorMovement) -> None:
        movement = aMoterMovement.movement_value
        
        if movement is None or movement == 0:
            self.__motor.throttle = movement
            return

        # Target RPM based on movement enum
        target_rpm = 65 if movement >= 0.1 else -65
        
        self.__current_throttle = self.__encoder.pi_controller(target_rpm, self.__current_throttle)
        self.__motor.throttle = self.__current_throttle

    def stop(self):
        self.__current_throttle = MotorMovement.LOCKED.movement_value
        self.__motor.throttle = MotorMovement.LOCKED.movement_value