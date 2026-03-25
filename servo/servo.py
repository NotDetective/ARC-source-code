from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory 
from time import sleep

factory = PiGPIOFactory()

hullServo = AngularServo(13, min_angle=-90, max_angle=90, pin_factory=factory)
shovelServo = AngularServo(19, min_angle=-90, max_angle=90, pin_factory=factory)


try:
    print("set starting positions")
    hullServo.angle =  -90
    shovelServo.angle = 90
    sleep(2)
    
    while True:
        print("start pick up")
        shovelServo.angle = 20
        sleep(3)
        hullServo.angle = 20
        sleep(3)
        
        print("return to starting position")
        hullServo.angle =  -90
        shovelServo.angle = 90
        sleep(7)
        
except KeyboardInterrupt:
    print("\nShutting down.")
    hullServo.detach()
    shovelServo.detach()