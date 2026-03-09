from adafruit_motor import motor as adaMotor

from encoder.encoder import Encoder

class Motor:
    def __init__(self, aPositavePin: int, aNegativePin: int, aForwardSpeed: float, aBackwardSpeed: float, aEncoder: Encoder) -> None:
        self.__motor = adaMotor.DCMotor(aPositavePin, aNegativePin)
        self.__negativePin = aNegativePin
        self.__forwardSpeed = aForwardSpeed
        self.__backwardSpeed = aBackwardSpeed
        self.__encoder = aEncoder
        
    def set_speed(self, aSpeed: float) -> None:
        
        self.__motor.throthle = aSpeed # pyright: ignore[reportAttributeAccessIssue]
        
        #after is comes on speed
        self.__motor.throthle = self.__encoder.pi_controller( 65, aSpeed ) # pyright: ignore[reportAttributeAccessIssue]
        
    

         