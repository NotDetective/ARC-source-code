from motor.motor import Motor
from motor.motorMovement import MotorMovement
from moveCommand import MoveCommand

class ForwardsCommand(MoveCommand):
    
    def motor_command(self, FLMotor: Motor, FRMotor: Motor, BLMotor: Motor, BRMotor: Motor):
        FLMotor.set_motor_movement(MotorMovement.FORWARDS)
        FRMotor.set_motor_movement(MotorMovement.FORWARDS)
        BLMotor.set_motor_movement(MotorMovement.FORWARDS)
        BRMotor.set_motor_movement(MotorMovement.FORWARDS)