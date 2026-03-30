from gpiozero import DistanceSensor
import time

sonar = DistanceSensor(echo=18, trigger=23)

while True:
    print(sonar.distance)
    time.sleep(0.5)