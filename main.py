import board
import lgpio
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from camera.camera import MyCamera as Camera
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.backwardsCommand import BackwardsCommand


i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

# cam = Camera()
# cam.start_camera()

motorController = MotorController(pca, chip)

# motorController.give_move_command(ForwardsCommand(), 200)

motorController.give_move_command(BackwardsCommand(), 200)


try: 
    print()
except:
    motorController.stop_all()

