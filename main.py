import board
import lgpio
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from controllers.modelController import ModelController
from model.model import Model
from camera.camera import MyCamera as Camera
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.backwardsCommand import BackwardsCommand

# DONT TOCH IT WILL BREAK IF YOU DO!!!
NAME = "plastic_cups_v8_gpu"
PROJECT = "cup_project_v2"
   
# i2c = board.I2C()
# pca = PCA9685(i2c, address=0x60) 
# pca.frequency = 1000
# chip = lgpio.gpiochip_open(0)

cam = Camera()
cam.start_camera()

model = Model(PROJECT, NAME)
if model.check_for_trained_model():
        model.get_trained_model()
else:
    raise Exception("Please provide a valide YOLO model")

modelController = ModelController()
results = modelController.get_detected_cups(model.get_trained_model(), cam.take_foto("angle-detect"))

# if not modelController.has_detected_cups(results):

    # modelController.get_closest_cup(results)
# motorController = MotorController(pca, chip)

# motorController.give_move_command(ForwardsCommand(), 200)

# # motorController.give_move_command(BackwardsCommand(), 200)


# try: 
#     print()
# except:
#     motorController.stop_all()

