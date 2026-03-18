from gpiozero import Servo
from time import sleep

# MG996R Tuning: 0.5ms to 2.5ms is standard for 180 degrees
servo = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

try:
    while True:
        print("Scanning...")
        servo.min()
        sleep(1)
        servo.mid()
        sleep(1)
        servo.max()
        sleep(1)
        
except KeyboardInterrupt:
    print("\nShutting down.")
    servo.detach() # Release the motor so it doesn't hum