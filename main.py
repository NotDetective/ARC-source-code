import board
import lgpio
import time
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from controllers.modelController import ModelController
from controllers.colorController import ColorController
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand
from moveCommands.counterClockwiseCommand import CounterClockwiseCommand
from model.model import Model
from camera.camera import MyCamera as Camera

def get_rotation_steps(degrees, rpm=65, track_width=20, wheel_radius=3):
    rps = rpm / 60
    seconds_for_360 = (track_width / wheel_radius) / rps
    
    target_seconds = (degrees / 360) * seconds_for_360
    
    steps = target_seconds / 0.05
    return int(steps)

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
    
    while True:        
        image = cam.take_foto("find-cup")
        results = model_controller.get_detected_cups(trained_model, image)    
        if not model_controller.has_detected_cups(results):
            print("end")
            break
        else:
            motor_controller.give_move_command(ClockwiseCommand(), int(get_rotation_steps(90) * 1.8))
    
except:
    motor_controller.stop_all()
    