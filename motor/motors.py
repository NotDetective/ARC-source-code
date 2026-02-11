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

def PiController(target_Pulses, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay):
    for index in pulse_counts:
        # 1. Calculate the error (Difference between desired speed and actual speed)
        # We use the absolute count because pulses are usually unsigned increments
        actual_pulses = pulse_counts[index]
        error = target_Pulses[index] - actual_pulses
        
        # 2. Accumulate Integral error
        integral[index] += error
        
        # 3. Calculate adjustment (The PI formula)
        adjustment = (Kp * error) + (Ki * integral[index])
        
        # 4. Update motor speed (Incrementally update current speed rather than jumping)
        # This prevents jerky movements
        new_speed = motorSpeeds[index] + adjustment
        motorSpeeds[index] = max(-1.0, min(1.0, new_speed))
        
        # 5. Decay integral to prevent "windup"
        integral[index] *= integralDecay
        
        # 6. Reset counts for the NEXT interval measurement
        pulse_counts[index] = 0

# handle Interrupts
for index, device in encoder_devices.items():
    # lamba d=index is needed to capture the current value of index in the loop
    device.when_activated = lambda d=index: count_pulse(d) # trigger on rising edge
    device.when_deactivated = lambda d=index: count_pulse(d) # trigger on falling edge

while True: 
    PiController(targetPulses, pulse_counts, integral, motorSpeeds, Kp, Ki, integralDecay)
    
    for index in motors:
        motors[index].throttle = motorSpeeds[index]
        print(f"{index} Speed: {motorSpeeds[index]:.2f} | Pulses: {pulse_counts[index]}")
            
    sleep(0.1)
    
    
