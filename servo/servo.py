import time
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# 1. Setup I2C bus (SDA/SCL pins are 26/27 on your U2 chip)
i2c = board.I2C()

# 2. Initialize the PCA9685 PWM Driver
pca = PCA9685(i2c, address=0x60)  # Default I2C address for PCA9685
pca.frequency = 50  # Servos typically run at 50Hz

# 3. Initialize Servo on PWM0 (J2) and PWM1 (J3)
# Note: min_pulse and max_pulse are usually 500 to 2500 for full range
servo_sg90 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)
# servo_mg996r = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)

def test_range(servo_obj, name):
    print(f"Testing {name}...")
    servo_obj.angle = 0
    time.sleep(1)
    servo_obj.angle = 180
    time.sleep(1)
    servo_obj.angle = 90 # Center it

try:
    test_range(servo_sg90, "SG90 on PWM0")
    # test_range(servo_mg996r, "MG996R on PWM1")
finally:
    pca.deinit()