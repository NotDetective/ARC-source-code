import RPi.GPIO as GPIO
import subprocess
import os
import time

# Configuration
BUTTON_PIN = 17  # Change this to your GPIO pin number
MAIN_SCRIPT = "main.py"
VENV_FILE = "motor-env"

# Setup
GPIO.setmode(GPIO.BCM)
# Using internal pull-up resistor (button connects Pin 17 to Ground)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def run_main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, MAIN_SCRIPT)
    venv_path = os.path.join(dir_path, f"{VENV_FILE}/bin/python3")

    if os.path.exists(venv_path):
        print(f"Launching with venv: {venv_path}")
        subprocess.run([venv_path, script_path])
    else:
        print(f"Error: Virtual environment not found at {venv_path}")
        
try:
    print("Waiting for button press...")
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == False:  
            run_main()
            # Debounce/Delay to prevent multiple triggers
            time.sleep(2) 
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()