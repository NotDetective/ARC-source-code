import board
from time import sleep
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

i2c = board.I2C()

pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000

motors = { 
    "BL": motor.DCMotor(pca.channels[8], pca.channels[9]), 
    "BR": motor.DCMotor(pca.channels[10], pca.channels[11]), 
    "FL": motor.DCMotor(pca.channels[12], pca.channels[13]), 
    "FR": motor.DCMotor(pca.channels[14], pca.channels[15]) 
}

print("forward")
for m in motors.values():
    m.throttle = 0.3

sleep(9)

# print("backward")
# for m in motors.values():
#     m.throttle = -1.0

sleep(2)

print("stop")
for m in motors.values():
    m.throttle = 0