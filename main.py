import board
import lgpio
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from camera.camera import MyCamera as Camera
from move.forwardsCommand import ForwardsCommand
from move.stopCommand import StopCommand


i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

cam = Camera()
cam.start_camera()

motorController = MotorController(pca, chip)
motorController.give_move_command(ForwardsCommand(), 5000)
