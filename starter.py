import lgpio
import subprocess
import os
import time

# Configuration
BUTTON_PIN = 24
MAIN_SCRIPT = "main.py"
VENV_FILE = "motor-env"

# Setup lgpio
chip = lgpio.gpiochip_open(0)

# Claim the pin as an input, detect falling edges (button press), and enable pull-up resistor
lgpio.gpio_claim_alert(chip, BUTTON_PIN, lgpio.FALLING_EDGE, lgpio.SET_PULL_UP)


# The callback function
def run_main(chip, gpio, level, tick):
    print("\n[+] Button pressed! Initiating launch sequence...")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, MAIN_SCRIPT)
    venv_path = os.path.join(dir_path, f"{VENV_FILE}/bin/python3")

    if os.path.exists(venv_path):
        print(f"Launching with venv: {venv_path}")
        # This will block and run the robot script until it finishes or crashes
        subprocess.run([venv_path, script_path])
        print("\n[*] Robot script finished. Waiting for next button press...")
    else:
        print(f"[!] Error: Virtual environment not found at {venv_path}")


try:
    print(f"System ready. Waiting for button press on GPIO {BUTTON_PIN}...")

    # Register the callback function to the pin
    # lgpio handles the interrupt in the background
    lgpio.callback(chip, BUTTON_PIN, lgpio.FALLING_EDGE, func=run_main)

    # Keep the script alive
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[!] Shutting down launcher...")
finally:
    # ALWAYS clean up
    lgpio.gpiochip_close(chip)