from operator import index
import board
import lgpio
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000
chip = lgpio.gpiochip_open(0)

# enable motor pins
motors = { 
    "BL": motor.DCMotor(pca.channels[8], pca.channels[9]), 
    "BR": motor.DCMotor(pca.channels[10], pca.channels[11]), 
    "FL": motor.DCMotor(pca.channels[12], pca.channels[13]), 
    "FR": motor.DCMotor(pca.channels[14], pca.channels[15]) 
}

# encoder pins
encoder_pins = {
    "BL": 17,
    "BR": 27,
    "FL": 22,
    "FR": 23
}

pulse_counts = {"BL": 0, "BR": 0, "FL": 0, "FR": 0}
motorSpeeds = {"BL": 0.46,"BR": 0.33,"FL": 0.47,"FR": 0.35}
targetRPM = {"BL": 65,"BR": 65,"FL": 65,"FR": 65}
integral = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}

Kp = 0.0005
Ki = 0.0

integralDecay = 1.0

dt = 0.05
currentRPM = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}
# ISR
def count_pulse_callback(chip, gpio, level, tick): # chip = gpiochip, gpio = pin number, level = 0 or 1, tick = timestamp of event
    for key, pin in encoder_pins.items(): # check which encoder triggered the interrupt
        # print(f"ticks {tick}")
        if gpio == pin: # if the interrupt is from this encoder pin
            pulse_counts[key] += 1 # increment the pulse count for that motor

# initialize encoder pins and set up interrupts
for side, pin in encoder_pins.items(): 
    lgpio.gpio_claim_alert(chip, pin, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP) # claim the GPIO pin for input lgpio.gpio_set_mode(chip, pin, lgpio.GPIO_MODE_INPUT) # set the pin as input lgpio.gpio_set_pull(chip, pin, lgpio.GPIO_PULL_UP) # enable pull-up resistor lgpio.gpio_set_alert_func(chip, pin, count_pulse_callback) # set the interrupt handler for this pin
    lgpio.callback(chip, pin, lgpio.BOTH_EDGES, func=count_pulse_callback) # register the callback function for both rising and falling edges


def PiController(targetPWM, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay):
    for index in pulse_counts:
        currentRPM[index] = ((pulse_counts[index] / 1080) * (60 / dt))
        error = targetPWM[index] - currentRPM[index]
        integral[index] = max(-50, min(50, integral[index] + error))
        adjustment = Kp * error + Ki * integral[index]
        motorSpeeds[index] = max(-1.0, min(1.0, motorSpeeds[index] + adjustment))
        integral[index] *= integralDecay
        pulse_counts[index] = 0

# startup time
for index in motors:
    motors[index].throttle = motorSpeeds[index]

time.sleep(dt * 5)
for index in motors:
    pulse_counts[index] = 0

for i in range(200):
    print(currentRPM)
    PiController(targetRPM, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay)
    
    for index in motors:
        motors[index].throttle = motorSpeeds[index]

    time.sleep(dt)
for index in motors:
    motors[index].throttle = 0.0


    
    
