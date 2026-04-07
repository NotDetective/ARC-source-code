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

        # --- Constants (Untouched) ---
        self.IMG_WIDTH = 4608
        self.CENTER_POINT = self.IMG_WIDTH // 2
        self.MARGIN = 150
        self.DEADZONE = 60

        self.MIN_COLLECT_DISTANCE = 16
        self.ALIGN_DISTANCE = 16
        self.COLLECT_THRESHOLD = 23

        self.GOAL_SIZE_THRESHOLD = 0.45 * 1000000
        self.BASE_RPM = 60
        self.MAX_CORRECTION = 40

        # --- Memory / Grace Period Variables ---
        self.last_valid_target_time = 0
        self.last_valid_x = None
        self.last_valid_size = 0
        self.VISION_GRACE_PERIOD = 1.5  # Seconds to remember the cup after it vanishes

    def run_robot_process(self):
        x, size = self.vision.get_data()
        current_cmd = self.motor_ctrl.get_current_command()
        is_moving = self.motor_ctrl.has_active_command()
        current_time = time.time()

        # Update memory ONLY if we currently see a VALID target
        if x is not None and size > self.GOAL_SIZE_THRESHOLD:
            self.last_valid_target_time = current_time
            self.last_valid_x = x
            self.last_valid_size = size

        # Check if we are within the grace period
        is_target_recently_seen = False
        if self.last_valid_target_time > 0:  # Only check if we've actually seen a target before
            time_since_last_seen = current_time - self.last_valid_target_time
            if time_since_last_seen < self.VISION_GRACE_PERIOD:
                is_target_recently_seen = True
            else:
                # Grace period expired, clear memory
                self.last_valid_target_time = 0
                self.last_valid_x = None
                self.last_valid_size = 0

        # 1. PRIORITY: TARGET REACHED (Using current vision OR recent memory)
        if (x is not None and size > self.GOAL_SIZE_THRESHOLD) or is_target_recently_seen:
            # Use current x if available, otherwise rely on the remembered x
            target_x = x if x is not None else self.last_valid_x

            # Sanity check: Ensure target_x is valid before proceeding
            if target_x is not None:
                return self.handle_target_reached(target_x, current_cmd, is_moving)

        # 2. PRIORITY: OBSTACLE AVOIDANCE
        obstacle_action = self.handle_obstacle_avoidance(current_cmd, is_moving)
        if obstacle_action:
            return obstacle_action

        # 3. PRIORITY: SEARCH
        if x is None and not is_target_recently_seen:
            return self.handle_search(current_cmd, is_moving)

        # 4. PRIORITY: APPROACH
        if x is not None or is_target_recently_seen:
            # Use current x if available, otherwise use remembered x
            target_x = x if x is not None else self.last_valid_x
            if target_x is not None:
                return self.handle_approach(target_x, current_cmd)

        return None

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
        self.motor_ctrl.reset_all_motors_rpm()

        error = x - self.CENTER_POINT
        dist_fm = self.sonar_ctrl.get_sonar_distance("FM")
        dist_fl = self.sonar_ctrl.get_sonar_distance("FL")
        dist_fr = self.sonar_ctrl.get_sonar_distance("FR")

        # 1. THE SONAR SKIP
        if self.MIN_COLLECT_DISTANCE < dist_fm < self.COLLECT_THRESHOLD:
            print(f"Bypassing alignment. Sonar confirmed cup at {dist_fm}cm.")
            self.motor_ctrl.stop_movement()
            self.collect_cup()
            self.last_valid_target_time = 0  # WIPE MEMORY
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
            self.last_valid_target_time = 0  # WIPE MEMORY
            return "COLLECTING_VISION"

        # 4. Precision Pivot
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
        print("--- Sequence Start ---")
        self.motor_ctrl.stop_movement()
        self.motor_ctrl.reset_all_motors_rpm()

        time.sleep(0.2)

        self.servo_ctrl.lower_mg996r()
        time.sleep(0.8)

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
        print("--- Sequence Complete ---")