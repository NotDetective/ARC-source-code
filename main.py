import board
import lgpio
import time
from adafruit_pca9685 import PCA9685
from controllers.motorController import MotorController
from controllers.modelController import ModelController
from controllers.colorController import ColorController
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from model.model import Model
from camera.camera import MyCamera as Camera

# --- CONFIGURATION ---
NAME = "plastic_cups_v8_gpu"
PROJECT = "cup_project_v2"
TARGET_HEX = "#b43384"
CENTER_THRESHOLD = 200  # Pixels of "wiggle room" before moving
IMAGE_WIDTH = 4608      # Adjust this to your camera's resolution

# --- HARDWARE SETUP ---
i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

motorController = MotorController(pca, chip)
cam = Camera()
cam.start_camera()

# --- MODEL SETUP ---
model = Model(PROJECT, NAME)
if model.check_for_trained_model():
    trained_model = model.get_trained_model()
else:
    raise Exception("Please provide a valid YOLO model")

modelController = ModelController()
colorController = ColorController()

print("Robot active. Searching for targets...")

while True:
    image = cam.take_foto("angle-detect")
    results = modelController.get_detected_cups(trained_model, image)
    box_data = modelController.get_biggest_box_boundaries(results)
    all_color_blobs = colorController.find_hex_object(image, TARGET_HEX)

    target_x = None

    # Filter blobs inside the detected cup box
    if box_data and all_color_blobs:
        x1, y1, x2, y2 = box_data
        filtered_blobs = [ (bx, by) for (bx, by) in all_color_blobs if x1 <= bx <= x2 and y1 <= by <= y2 ]
        
        if filtered_blobs:
            # Get the average X position of the detected blobs
            target_x = sum(b[0] for b in filtered_blobs) / len(filtered_blobs)

    # --- CENTERING LOGIC ---
    if target_x is not None:
        screen_center = IMAGE_WIDTH / 2
        error = target_x - screen_center

        print(error * -1)

        if abs(error) <= CENTER_THRESHOLD:
            print("Target Centered! Moving Forward...")
            # motorController.give_move_command(ForwardsCommand(), 100)
        elif error > 0:
            print(f"Target is Right (error: {error}). Turning Right...")
            motorController.give_move_command(RightCommand(), int(error/50))
            # motorController.turn_right(speed=150) # Replace with your actual turn command
        else:
            print(f"Target is Left (error: {error}). Turning Left...")
            motorController.give_move_command(LeftCommand(), int((error * -1) /50)  )
            # motorController.turn_left(speed=150)  # Replace with your actual turn command
    else:
        print("Searching for cup...")
        # Optional: motorController.stop() 

    time.sleep(0.1) # Reduced sleep for better responsiveness