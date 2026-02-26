from motor.motor import Motor
from encoder.encoder import Encoder

class MotorController:

    def __init__(self, aPca):
        self.__motors = {
            "BL": Motor(
                aPca.channels[8],
                aPca.channels[9],
                0.0,  # initial forward speed
                0.0,  # initial backward speed
                Encoder(17)
            ),
            "BR": Motor(
                aPca.channels[10],
                aPca.channels[11],
                0.0,  # initial forward speed
                0.0,  # initial backward speed
                Encoder(27)
            ),
            "FL": Motor(
                aPca.channels[12],
                aPca.channels[13],
                0.0,  # initial forward speed
                0.0,  # initial backward speed
                Encoder(22)
            ),
            "FR": Motor(
                aPca.channels[14],
                aPca.channels[15],
                0.0,  # initial forward speed
                0.0,  # initial backward speed
                Encoder(23)
            )
        }
    
    def give_move_command(self):
        pass

