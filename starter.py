import lgpio
import subprocess
import os
import time
import signal

# --- Configuration ---
BUTTON_PIN = 24
MAIN_SCRIPT = "starter.py"  # Ensure this matches your robot filename
VENV_FILE = "motor-env"

process = None
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_alert(chip, BUTTON_PIN, lgpio.FALLING_EDGE, lgpio.SET_PULL_UP)


def toggle_robot(chip, gpio, level, tick):
    global process

    # If robot is running, stop it

    if process is not None and process.poll() is None:
        print("\n[!] Hold Confirmed: Stopping Robot...")
        # Send custom signal so the OS doesn't accidentally trigger this
        process.send_signal(signal.SIGUSR1)
        process.wait()
        process = None
        print("[*] Robot is now OFF.")

    # If robot is stopped, start it
    else:
        print("\n[+] Button Pressed: Starting Robot...")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(dir_path, "main.py")  # Your actual robot code
        venv_path = os.path.join(dir_path, f"{VENV_FILE}/bin/python3")

        if os.path.exists(venv_path):
            # Launch in background
            process = subprocess.Popen([venv_path, script_path])
            print(f"[*] Robot is now RUNNING (PID: {process.pid})")
        else:
            print(f"[!] Error: Virtual environment not found at {venv_path}")


try:
    print(f"--- Launcher Active ---")
    print(f"Waiting for button on GPIO {BUTTON_PIN}...")

    lgpio.callback(chip, BUTTON_PIN, lgpio.FALLING_EDGE, func=toggle_robot)

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[!] Launcher shutting down...")
    if process and process.poll() is None:
        process.terminate()
finally:
    lgpio.gpiochip_close(chip)