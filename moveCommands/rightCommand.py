

from motor.motor import Motor
from motor.motorMovement import MotorMovement
from moveCommands.moveCommand import MoveCommand

class RightCommand(MoveCommand):
    
    def motor_command(self, FLMotor: Motor, FRMotor: Motor, BLMotor: Motor, BRMotor: Motor):
        FLMotor.set_motor_movement(MotorMovement.FORWARDS)
        FRMotor.set_motor_movement(MotorMovement.BACKWARDS)
        BLMotor.set_motor_movement(MotorMovement.BACKWARDS)
        BRMotor.set_motor_movement(MotorMovement.FORWARDS)