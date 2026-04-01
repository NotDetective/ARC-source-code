from adafruit_motor import servo
import time

class ServoController:

    def __init__(self, pca):
        self.pca = pca
        self.servo_sg90 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)
        self.servo_mg996r = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)

        self.set_pca()
        self.open_sg90()
        time.sleep(0.8)
        self.raise_mg996r()
        time.sleep(0.8)
        self.return_pca()

    def __move_servo_slowly(self, servo_obj, start_angle, end_angle, step_delay=0.005):
        # Determine the direction of movement (up or down)
        step = 1 if end_angle > start_angle else -1

        for angle in range(start_angle, end_angle + step, step):
            servo_obj.angle = angle
            time.sleep(step_delay)

    def set_pca(self):
        print("fuck no")
        # if self.pca.frequency != 50:
        #     self.pca.frequency = 50

    def return_pca(self):
        print("fuck no 2")
        # if self.pca.frequency != 1000:
        #     self.pca.frequency = 1000
        #
        #     for i in range(16):
        #         self.pca.channels[i].duty_cycle = 0

    def lower_mg996r(self):
        self.servo_mg996r.angle = 55

    def raise_mg996r(self):
        self.servo_mg996r.angle = 170

    def open_sg90(self):
        self.__move_servo_slowly(self.servo_sg90, 150, 100, 0.005)

    def close_sg90(self):
        self.__move_servo_slowly(self.servo_sg90, 100, 150, 0.005)



