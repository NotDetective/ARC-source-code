from gpiozero import DistanceSensor
ultrasonic = [
    DistanceSensor(echo=24, trigger=25), 
    DistanceSensor(echo=14, trigger=15)
    ]
while True:
    for i in range(2):
        print (ultrasonic[i].distance*100)
    print()