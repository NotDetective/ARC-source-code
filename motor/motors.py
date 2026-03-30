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
    "FL": motor.DCMotor(pca.channels[8], pca.channels[9]), 
    "BL": motor.DCMotor(pca.channels[11], pca.channels[10]), 
    "FR": motor.DCMotor(pca.channels[13], pca.channels[12]), 
    "BR": motor.DCMotor(pca.channels[14], pca.channels[15]) 
}

# encoder pins
encoder_pins = {
    "FL": 1,
    "BL": 7,
    "FR": 8,
    "BR": 25
}

pulse_counts = {"BL": 0, "BR": 0, "FL": 0, "FR": 0}
# forwards
# motorSpeeds = {"BL": 0.46,"BR": 0.33,"FL": 0.47,"FR": 0.37} # old values

# motorSpeeds = {"FL": 0.40, "BL": 0.36, "FR": 0.30, "BR": 0.40}
# motorSpeeds = {"FL": 0.47, "BL": 0.37, "FR": 0.37,"BR": 0.46} new old values, not correct
# motorSpeeds = {"FL": -0.30, "BL": -0.33 , "FR": -0.35,"BR": -0.42}

# backwards
# motorSpeeds = {"BL": -0.37,"BR": -0.42,"FL": -0.35,"FR": -0.39}
# turn cw
motorSpeeds = {"BL": 0.46,"BR": -0.42,"FL": -0.35,"FR": 0.37}
targetRPM = {"FL": -65,"BL": 65,"FR": 65 ,"BR": -65}
integral = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}
currentRPM = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}

Kp = 0.0005
dt = 0.05

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


def PiController(targetPWM, pulse_counts, integral, motorSpeeds, Kp):
    for index in pulse_counts:
        currentRPM[index] = ((pulse_counts[index] / 1080) * (60 / dt))
        if targetPWM[index] > 0:
            error = targetPWM[index] - currentRPM[index]
        elif targetPWM[index] < 0:
            error = targetPWM[index] + currentRPM[index]
        else:            
            error = 0
        adjustment = Kp * error
        motorSpeeds[index] = max(-1.0, min(1.0, motorSpeeds[index] + adjustment))
        pulse_counts[index] = 0

# startup time
for index in motors:
    motors[index].throttle = motorSpeeds[index]

time.sleep(dt * 5)
for index in motors:
    pulse_counts[index] = 0

try:
    for i in range(200000000):
        print(currentRPM)
        PiController(targetRPM, pulse_counts, integral, motorSpeeds, Kp)
        
        for index in motors:
            motors[index].throttle = motorSpeeds[index]

        time.sleep(dt)
    for index in motors:
        motors[index].throttle = 0.0
except KeyboardInterrupt:
    for index in motors:
        motors[index].throttle = 0.0

    
    
