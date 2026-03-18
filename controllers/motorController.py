import time
import threading
from motor.motor import Motor
from encoder.encoder import Encoder
from moveCommands.moveCommand import MoveCommand

class MotorController:
    def __init__(self, aPca, aChip):
        self._stop_event = threading.Event()
        self._move_thread = None
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
        self.__dt = 0.05
        
    def has_active_command(self):
        return self._stop_event.is_set()
    
    def set_move_command(self, aCommand: MoveCommand):
        self._stop_event.set() 
        
        self._move_thread = threading.Thread(
            target=self._execute_move_loop, 
            args=(aCommand, ),
            daemon=True 
        )
        self._move_thread.start()

    def _execute_move_loop(self, aCommand: MoveCommand):
        aCommand.motor_command(
            self.__motors["FL"], self.__motors["FR"], 
            self.__motors["BL"], self.__motors["BR"]
        )

        i = 0
        while self._stop_event.is_set():    
           
            if i <= 6:
                i += 1                     
            
            for motor in self.__motors.values():
                motor.run_motor(i) 
            
            time.sleep(self.__dt)
                    
    def stop_movement(self):
        self._stop_event.clear()
        self.stop_all()
        
    def stop_all(self):
        for motor in self.__motors.values():
            motor.stop()

