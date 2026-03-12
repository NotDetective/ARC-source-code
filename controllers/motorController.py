import time

from motor.motor import Motor
from encoder.encoder import Encoder
from moveCommands.moveCommand import MoveCommand

class MotorController:

# forwards:
# BL: 0.46
# BR: 0.33
# FL: 0.47
# FR: 0.35

# Backwards:
# BL: -0.37
# BR: -0.42
# FL: -0.35
# FR: -0.39

    def __init__(self, aPca, aChip):
        self.__motors = {
            "BL": Motor(
                aPca.channels[8],
                aPca.channels[9],
                0.46,  # initial forward speed
                -0.37,  # initial backward speed
                Encoder(17, aChip)
            ),
            "BR": Motor(
                aPca.channels[10],
                aPca.channels[11],
                0.33,  # initial forward speed
                -0.42,  # initial backward speed
                Encoder(27, aChip)
            ),
            "FL": Motor(
                aPca.channels[12],
                aPca.channels[13],
                0.47,  # initial forward speed
                -0.35,  # initial backward speed
                Encoder(22, aChip)
            ),
            "FR": Motor(
                aPca.channels[14],
                aPca.channels[15],
                0.35,  # initial forward speed
                -0.39,  # initial backward speed
                Encoder(23, aChip)
            )
        }
        self.__running = False
        self.__dt = 0.05
    
    def give_move_command(self, aCommand: MoveCommand, duration_steps=200):
        aCommand.motor_command(
            self.__motors["FL"], self.__motors["FR"], 
            self.__motors["BL"], self.__motors["BR"]
        )

        for i in range(1, duration_steps + 1):
            for motor in self.__motors.values():
                motor.run_motor(i) 
            
            time.sleep(self.__dt)
            
        self.stop_all()
        
    def stop_all(self):
        for motor in self.__motors.values():
            motor.stop()

