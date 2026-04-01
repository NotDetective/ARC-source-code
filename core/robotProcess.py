import time
from moveCommands.backwardsCommand import BackwardsCommand
from moveCommands.counterClockwiseCommand import CounterClockwiseCommand
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand


class RobotProcess:
    def __init__(self, motor_ctrl, sonar_ctrl, servo_ctrl, vision, pca, target_hex):
        self.motor_ctrl = motor_ctrl
        self.sonar_ctrl = sonar_ctrl
        self.servo_ctrl = servo_ctrl
        self.vision = vision
        self.pca = pca
        self.target_hex = target_hex

        # Sensor Calibration
        self.sonar_ctrl.set_sonar_trigger_distance("L", 15)
        self.sonar_ctrl.set_sonar_trigger_distance("R", 15)
        self.sonar_ctrl.set_sonar_trigger_distance("FM", 20)

        # --- Constants ---
        self.IMG_WIDTH = 4608
        self.CENTER_POINT = self.IMG_WIDTH // 2
        self.MARGIN = 150  # Widened slightly to prevent "hunting" for center
        self.DEADZONE = 60

        self.ALIGN_DISTANCE = 16
        self.COLLECT_THRESHOLD = 23  # Triggers the grab

        self.GOAL_SIZE_THRESHOLD = 0.45 * 1000000
        self.BASE_RPM = 60
        self.MAX_CORRECTION = 40

    def run_robot_process(self):
        x, size = self.vision.get_data()
        current_cmd = self.motor_ctrl.get_current_command()
        is_moving = self.motor_ctrl.has_active_command()

        # 1. PRIORITY: TARGET REACHED
        if x is not None and size > self.GOAL_SIZE_THRESHOLD:
            return self.handle_target_reached(x, current_cmd, is_moving)

        # 2. PRIORITY: OBSTACLE AVOIDANCE
        obstacle_action = self.handle_obstacle_avoidance(current_cmd, is_moving)
        if obstacle_action:
            return obstacle_action

        # 3. PRIORITY: SEARCH
        if x is None:
            return self.handle_search(current_cmd, is_moving)

        # 4. PRIORITY: APPROACH
        return self.handle_approach(x, current_cmd)

    def handle_obstacle_avoidance(self, current_cmd, is_moving):
        l_blocked = self.sonar_ctrl.is_blocked("L") or self.sonar_ctrl.is_blocked("FL")
        r_blocked = self.sonar_ctrl.is_blocked("R") or self.sonar_ctrl.is_blocked("FR")
        f_blocked = self.sonar_ctrl.is_blocked("FM")

        if f_blocked or r_blocked:
            if not isinstance(current_cmd, LeftCommand):
                self.motor_ctrl.set_move_command(LeftCommand())
            return "EVADING_LEFT"
        if l_blocked:
            if not isinstance(current_cmd, RightCommand):
                self.motor_ctrl.set_move_command(RightCommand())
            return "EVADING_RIGHT"
        return None

    def handle_approach(self, x, current_cmd):
        if not isinstance(current_cmd, ForwardsCommand):
            self.motor_ctrl.set_move_command(ForwardsCommand())
        self.apply_proportional_steering(x)
        return "APPROACHING"

    def apply_proportional_steering(self, target_x):
        error = target_x - self.CENTER_POINT
        if abs(error) < self.DEADZONE:
            self.motor_ctrl.reset_all_motors_rpm()
            return

        correction = int((abs(error) / self.CENTER_POINT) * self.MAX_CORRECTION)
        if error < 0:  # Target Left
            self.motor_ctrl.set_motor_rpm("FL", self.BASE_RPM - correction)
            self.motor_ctrl.set_motor_rpm("BL", self.BASE_RPM - correction)
            self.motor_ctrl.set_motor_rpm("FR", self.BASE_RPM + correction)
            self.motor_ctrl.set_motor_rpm("BR", self.BASE_RPM + correction)
        else:  # Target Right
            self.motor_ctrl.set_motor_rpm("FR", self.BASE_RPM - correction)
            self.motor_ctrl.set_motor_rpm("BR", self.BASE_RPM - correction)
            self.motor_ctrl.set_motor_rpm("FL", self.BASE_RPM + correction)
            self.motor_ctrl.set_motor_rpm("BL", self.BASE_RPM + correction)

    def handle_target_reached(self, x, current_cmd, is_moving):
        """Alignment check with hard motor resets to stop the left-veer."""

        # --- CRITICAL FIX: Kill all previous steering RPMs immediately ---
        self.motor_ctrl.reset_all_motors_rpm()

        error = x - self.CENTER_POINT
        dist_fm = self.sonar_ctrl.get_sonar_distance("FM")
        dist_fl = self.sonar_ctrl.get_sonar_distance("FL")
        dist_fr = self.sonar_ctrl.get_sonar_distance("FR")

        # 1. THE SONAR SKIP: If the sensor sees it, GRAB. Stop checking vision.
        if 5 < dist_fm < self.COLLECT_THRESHOLD:
            print(f"Bypassing alignment. Sonar confirmed cup at {dist_fm}cm.")
            self.motor_ctrl.stop_movement()
            self.collect_cup()
            return "COLLECTING_SONAR"

        # 2. Safety Backwards
        if dist_fm < self.ALIGN_DISTANCE or dist_fl < self.ALIGN_DISTANCE or dist_fr < self.ALIGN_DISTANCE:
            if not isinstance(current_cmd, BackwardsCommand):
                self.motor_ctrl.set_move_command(BackwardsCommand())
            return "BACKING_UP"

        # 3. Final Alignment (Vision)
        if abs(error) <= self.MARGIN:
            self.motor_ctrl.stop_movement()
            self.collect_cup()
            return "COLLECTING_VISION"

        # 4. Precision Pivot (Low power to prevent overshoot)
        # We manually set RPM to 20 here to ensure it's balanced
        self.motor_ctrl.set_motor_rpm("ALL", 20)
        if error > 0:
            if not isinstance(current_cmd, ClockwiseCommand):
                self.motor_ctrl.set_move_command(ClockwiseCommand())
        else:
            if not isinstance(current_cmd, CounterClockwiseCommand):
                self.motor_ctrl.set_move_command(CounterClockwiseCommand())
        return "FINAL_ALIGNMENT"

    def handle_search(self, current_cmd, is_moving):
        if not isinstance(current_cmd, ClockwiseCommand):
            self.motor_ctrl.reset_all_motors_rpm()
            self.motor_ctrl.set_move_command(ClockwiseCommand())
        return "SEARCHING"

    def collect_cup(self):
        """Strict linear sequence. No steering allowed here."""
        print("--- Sequence Start ---")
        self.motor_ctrl.stop_movement()
        self.motor_ctrl.reset_all_motors_rpm()  # Force clean slate

        self.servo_ctrl.set_pca()
        time.sleep(0.2)

        self.servo_ctrl.lower_mg996r()
        time.sleep(0.8)

        # Linear push - reset RPM again just in case
        self.motor_ctrl.reset_all_motors_rpm()
        self.motor_ctrl.set_move_command(ForwardsCommand())
        time.sleep(0.7)
        self.motor_ctrl.stop_movement()

        self.servo_ctrl.close_sg90()
        time.sleep(1.0)
        self.servo_ctrl.raise_mg996r()
        time.sleep(1.0)
        self.servo_ctrl.open_sg90()
        time.sleep(0.5)

        self.servo_ctrl.return_pca()
        print("--- Sequence Complete ---")