import board
import lgpio
import traceback
from sys import exit
from adafruit_pca9685 import PCA9685
from robotProcess import RobotProcess
from controllers.motorController import MotorController
from controllers.modelController import ModelController
from controllers.colorController import ColorController
from controllers.sonarController import SonarController
from model.model import Model
from camera.camera import MyCamera as Camera

from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.backwardsCommand import BackwardsCommand

# --- CONFIGURATION ---
NAME = "plastic_cups_v8_gpu"
PROJECT = "cup_project_v2"
TARGET_HEX = "#b43384"
SCAN_TIMEOUT = 40.0 


# --- HARDWARE SETUP ---

try:
    i2c = board.I2C()
    pca = PCA9685(i2c, address=0x60)
except Exception as e:
    print("\n[!] FATAL ERROR: Could not connect to I2C port.")
    print(f"Details: {e}")
    print("-" * 40)
    print("TROUBLESHOOTING STEPS:")
    print("1. Does the robot have main power?")
    print("2. Is the motor shield powered independently?")
    print("3. Are the status LEDs on the motors illuminated?")
    print("-" * 40)
    exit(1)

pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

# --- MODEL SETUP ---
model = Model(PROJECT, NAME)
if model.check_for_trained_model():
    trained_model = model.get_trained_model()
else:
    raise Exception("Please provide a valid YOLO model")

motor_controller = MotorController(pca, chip)
model_controller = ModelController()
color_controller = ColorController()
sonar_controller = SonarController()
cam = Camera()  

# --- STARTS ---
cam.start_camera()

try:   
    robot_logic = RobotProcess(
        motor=motor_controller,
        model_ctrl=model_controller,
        color_ctrl=color_controller,
        sonar_ctrl=sonar_controller,
        model=trained_model,
        camera=cam,
        target_hex=TARGET_HEX,
        timeout=SCAN_TIMEOUT
    )

    # sonar_controller.set_sonar_active("L")
    # sonar_controller.start_sonars(motor_controller)

    # motor_controller.set_move_command(BackwardsCommand())

    i = 0
    while True:
        i += 1            
        robot_logic.run_state_logic()
        
        
        
except KeyboardInterrupt:
    motor_controller.stop_movement()
except Exception as e:
    motor_controller.stop_movement()
    print("--- FULL ERROR TRACEBACK ---")
    traceback.print_exc() 
    print("----------------------------")