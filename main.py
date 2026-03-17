import board
import lgpio
import time
import traceback
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from controllers.modelController import ModelController
from controllers.colorController import ColorController
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand
from moveCommands.counterClockwiseCommand import CounterClockwiseCommand
from model.model import Model
from camera.camera import MyCamera as Camera

# --- CONFIGURATION ---
NAME = "plastic_cups_v8_gpu"
PROJECT = "cup_project_v2"
TARGET_HEX = "#b43384"
CENTER_THRESHOLD = 250 
IMAGE_WIDTH = 4608     

# --- HARDWARE SETUP ---
i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

motor_controller = MotorController(pca, chip)
cam = Camera()
cam.start_camera()

# --- MODEL SETUP ---
model = Model(PROJECT, NAME)
if model.check_for_trained_model():
    trained_model = model.get_trained_model()
else:
    raise Exception("Please provide a valid YOLO model")

model_controller = ModelController()
color_controller = ColorController()


try:    
    # motor_controller.set_move_command(ForwardsCommand())
    while True:
        # all code here
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    motor_controller.stop_movement()
except Exception as e:
    motor_controller.stop_movement()
    print("--- FULL ERROR TRACEBACK ---")
    traceback.print_exc() 
    print("----------------------------")
    