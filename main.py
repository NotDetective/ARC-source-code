import board
import lgpio
import traceback
import time
import signal
import os
from adafruit_pca9685 import PCA9685
from controllers.servoController import ServoController
from core.robotProcess import RobotProcess
from controllers.motorController import MotorController
from controllers.sonarController import SonarController
from core.visionSystem import  VisionSystem
from camera.camera import MyCamera as Camera

# --- CONFIGURATION ---
NAME = "plastic_cups_v8_gpu"
PROJECT = "cup_project_v2"
TARGET_HEX = "#b43384"
USE_STREAMER = True

# --- Shutdown Handler ---
def handle_stop_signal(signum, frame):
    print("\n[!] Stop command received from Button Launcher...")
    raise KeyboardInterrupt

# Register to SIGUSR1 instead of SIGTERM
signal.signal(signal.SIGUSR1, handle_stop_signal)

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

pca.frequency = 300
chip = lgpio.gpiochip_open(0)

for i in range(16):
    pca.channels[i].duty_cycle = 0

# --- CONTROLLER SETUP ---
motor_controller = MotorController(pca, chip)
servo_controller = ServoController(pca)
sonar_controller = SonarController()
cam = Camera()
vision = VisionSystem(camera=cam, target_hex=TARGET_HEX)

# --- STARTS ---
cam.start_camera()
vision.start()

try:
    robot_logic = RobotProcess(
        motor_ctrl=motor_controller,
        sonar_ctrl=sonar_controller,
        servo_ctrl=servo_controller,
        vision=vision,
        pca=pca,
        target_hex=TARGET_HEX,
    )

    sonar_controller.set_sonars_active()
    sonar_controller.start_sonars()

    while True:
        robot_logic.run_robot_process()
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n[!] Stop button pressed: Cleaning up...")
    motor_controller.stop_movement()
    cam.stop_camera()

except Exception as e:
    print(f"[!!] Unexpected Error: {e}")
    motor_controller.stop_movement()
    traceback.print_exc()

finally:
    # This ensures the process actually dies so the launcher can start a new one
    print("[*] Robot process terminated.")
    os._exit(0)