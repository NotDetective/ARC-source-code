from motor.motor import Motor
from motor.motorMovement import MotorMovement
from moveCommands.moveCommand import MoveCommand

class BackwardsCommand(MoveCommand):
    
    def motor_command(self, FLMotor: Motor, FRMotor: Motor, BLMotor: Motor, BRMotor: Motor):
        FRMotor.set_motor_movement(MotorMovement.BACKWARDS)
        FLMotor.set_motor_movement(MotorMovement.BACKWARDS)
        BLMotor.set_motor_movement(MotorMovement.BACKWARDS)
        BRMotor.set_motor_movement(MotorMovement.BACKWARDS)