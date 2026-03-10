from abc import ABC, abstractmethod

class MoveCommand(ABC):
    
    @abstractmethod
    def motor_command(self, FLMotor, FRMotor, BLMotor, BRMotor):
        pass
       