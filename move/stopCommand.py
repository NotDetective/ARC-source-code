from motor.motor import Motor
from motor.motorMovement import MotorMovement
from moveCommand import MoveCommand

class StopCommand(MoveCommand):
    
    def motor_command(self, FLMotor: Motor, FRMotor: Motor, BLMotor: Motor, BRMotor: Motor):
        FLMotor.set_motor_movement(MotorMovement.LOCKED)
        FRMotor.set_motor_movement(MotorMovement.LOCKED)
        BLMotor.set_motor_movement(MotorMovement.LOCKED)
        BRMotor.set_motor_movement(MotorMovement.LOCKED)