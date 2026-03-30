import threading
import time

from sonar.sonar import Sonar


class SonarController:
    def __init__(self):
        self.__sonars = {
            "L": Sonar(echo=12, trigger=16),
            "R": Sonar(echo=18, trigger=23),
            "FL": Sonar(echo=20, trigger=6),
            "FM": Sonar(echo=21, trigger=26),
            "FR": Sonar(echo=4, trigger=17),
        }
        self.__running = False
        self.obstacles = {name: False for name in self.__sonars}
        self.__threads = []

    # In SonarController
    def __single_sonar_loop(self, name, sonar):
        while self.__running:
            if sonar.is_active():

                print( f"{name}: {sonar.is_triggerd()}")

                # If a front sensor is triggered, set a flag immediately
                if sonar.is_triggerd():
                    self.obstacles[name] = True
                    # If it's a front sensor, we can force a stop right here
                    if name in ["FM", "FL", "FR"]:
                        self.emergency_brake = True
                else:
                    self.obstacles[name] = False
            time.sleep(0.03)  # Faster polling

    def start_sonars(self):
        if not self.__running:
            self.__running = True
            for name, sonar in self.__sonars.items():
                t = threading.Thread(
                    target=self.__single_sonar_loop,
                    args=(name, sonar),
                    daemon=True
                )
                t.start()
                self.__threads.append(t)
            print(f"Started {len(self.__threads)} independent sonar threads.")

    def is_blocked(self, name):
        return self.obstacles.get(name, False)

    def set_sonars_active(self):
        for sonar in self.__sonars.values():
            sonar.set_active()

    def stop_all(self):
        self.__running = False
