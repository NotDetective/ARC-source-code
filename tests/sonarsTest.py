from gpiozero import DistanceSensor
import time

sonar = {
    "L": DistanceSensor(echo=12, trigger=16),
    "R": DistanceSensor(echo=18, trigger=23),
    "FL": DistanceSensor(echo=20, trigger=6),
    "FM": DistanceSensor(echo=21, trigger=26),
    "FR": DistanceSensor(echo=4, trigger=17),
}

while True:
    for key, sonar_sensor in sonar.items():
        print(f" {key}: {sonar_sensor.distance:.2f} ")

    print("-" * 20)

    time.sleep(1)