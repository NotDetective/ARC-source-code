import board
from time import sleep
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor
from gpiozero import DigitalInputDevice 

i2c = board.I2C()
pca = PCA9685(i2c, address=0x60) 
pca.frequency = 1000

# enable motor pins
motors = { 
    "BL": motor.DCMotor(pca.channels[8], pca.channels[9]), 
    "BR": motor.DCMotor(pca.channels[10], pca.channels[11]), 
    "FL": motor.DCMotor(pca.channels[12], pca.channels[13]), 
    "FR": motor.DCMotor(pca.channels[14], pca.channels[15]) 
}

# enable the interrupts on the GPIO pins
encoder_devices = {
    "BL": DigitalInputDevice(17, pull_up=True),
    "BR": DigitalInputDevice(27, pull_up=True),
    "FL": DigitalInputDevice(22, pull_up=True),
    "FR": DigitalInputDevice(23, pull_up=True)
}

pulse_counts = {"BL": 0, "BR": 0, "FL": 0, "FR": 0}
motorSpeeds = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}
targetPulses = {"BL": 250,"BR": 250,"FL": 250,"FR": 250}
integral = {"BL": 0.0,"BR": 0.0,"FL": 0.0,"FR": 0.0}

Kp = 0.01
Ki = 0.0

integralDecay = 1.0

#interrupt trigger
def count_pulse(target_key):
    pulse_counts[target_key] += 1

# handle Interrupts
for index, device in encoder_devices.items():
    # lamba d=index is needed to capture the current value of index in the loop
    device.when_activated = lambda d=index: count_pulse(d) # trigger on rising edge
    device.when_deactivated = lambda d=index: count_pulse(d) # trigger on falling edge

def PiController(target_Pulses, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay):
    for index in pulse_counts:
        if target_Pulses[index] > 0:
            error = target_Pulses[index] - pulse_counts[index]
        elif  target_Pulses[index] < 0:
            error = target_Pulses[index] + pulse_counts[index]
        else: 
            error = 0
        integral[index] += error
        adjustment = Kp * error + Ki * integral[index]
        print(f"Error: {error}, Integral: {integral[index]}, Adjustment: {adjustment}")
        motorSpeeds[index] = max(-1.0, min(1.0, adjustment))
        integral[index] *= integralDecay
        pulse_counts[index] = 0

while True: 

    PiController(targetPulses, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay)
    for index in motors:
        motors[index].throttle = motorSpeeds[index]
        #print(f"Target: {targetPulses[index]}, Count: {pulse_counts[index]}, Speed: {motorSpeeds[index]}").
    sleep(0.1)
    
    
