from adafruit_motor import servo
import time

class ServoController:

    def __init__(self, pca):
        self.pca = pca
        self.servo_sg90 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)
        self.servo_mg996r = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)

        self.SERVO_OPEN = 90
        self.SERVO_CLOSE = 150

        self.open_sg90()
        time.sleep(0.8)
        self.raise_mg996r()
        time.sleep(0.8)

    def __move_servo_slowly(self, servo_obj, start_angle, end_angle, step_delay=0.005):
        # Determine the direction of movement (up or down)
        step = 1 if end_angle > start_angle else -1

        for angle in range(start_angle, end_angle + step, step):
            servo_obj.angle = angle
            time.sleep(step_delay)

    def lower_mg996r(self):
        self.servo_mg996r.angle = 41

    def raise_mg996r(self):
        self.servo_mg996r.angle = 170

    def open_sg90(self):
        self.__move_servo_slowly(self.servo_sg90, self.SERVO_CLOSE, self.SERVO_OPEN, 0.005)

    def close_sg90(self):
        self.__move_servo_slowly(self.servo_sg90, self.SERVO_OPEN, self.SERVO_CLOSE, 0.005)



