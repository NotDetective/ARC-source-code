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
servo_mg996r = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)

def move_servo_slowly(servo_obj, start_angle, end_angle, step_delay=0.005):

    # Determine the direction of movement (up or down)
    step = 1 if end_angle > start_angle else -1
    
    for angle in range(start_angle, end_angle + step, step):
        servo_obj.angle = angle
        time.sleep(step_delay)

def test_range(sg90, mg996r):
    # mg996r.angle = 180
    # time.sleep(1)
    # move_servo_slowly(servo_sg90, 150, 100, 0.005)
    # time.sleep(1)
    mg996r.angle = 55
    time.sleep(1)
    move_servo_slowly(servo_sg90, 100, 150, 0.005)
    time.sleep(2)
    mg996r.angle = 170
    time.sleep(1)
    move_servo_slowly(servo_sg90, 150, 100, 0.005)
try:
    test_range(servo_sg90, servo_mg996r)
finally:
    pca.deinit()