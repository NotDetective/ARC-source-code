from adafruit_motor import motor as adaMotor

class Motor:
    def __init__(self, aPositavePin, aNegativePin, aForwardSpeed, aBackwardSpeed, aEncoder):
        self.__motor = adaMotor.DCMotor(aPositavePin, aNegativePin)
        self.__negativePin = aNegativePin
        self.__forwardSpeed = aForwardSpeed
        self.__backwardSpeed = aBackwardSpeed
        self.__encoder = aEncoder
        
    def set_speed(self, aSpeed):
        
        self.__motor.throthle = aSpeed
        
        #after is comes on speed
        self.__motor.throthle = self.__encoder.pi_controller( 65, aSpeed )
        
    

         