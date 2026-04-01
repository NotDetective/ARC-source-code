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

        self.sonar_ctrl.set_sonar_trigger_distance("L", 10)
        self.sonar_ctrl.set_sonar_trigger_distance("R", 10)

        # --- Constants (Optimized for 640x480) ---
        self.IMG_WIDTH = 4608
        self.CENTER_POINT = self.IMG_WIDTH // 2
        self.MARGIN = 140
        self.GOAL_SIZE = 0.45  # X10k Threshold to stop at the cup
        self.CORRECTION_RPM = 50

    def run_robot_process(self):
        """Main Brain: Decides priority based on current senses."""
        # 1. Gather all "Senses"
        x, size = self.vision.get_data()
        current_cmd = self.motor_ctrl.get_current_command()
        is_moving = self.motor_ctrl.has_active_command()

        if size > (self.GOAL_SIZE * 1000000):
            return self.handle_target_reached(x, current_cmd, is_moving)

        # PRIORITY 1: Safety (Obstacle Avoidance)
        # We check this first so we don't crash while trying to reach the cup
        obstacle_action = self.handle_obstacle_avoidance(current_cmd, is_moving)
        if obstacle_action:
            return obstacle_action

        # PRIORITY 3: Search for Target
        if x is None:
            return self.handle_search(current_cmd, is_moving)

        # PRIORITY 4: Normal Approach (Cup is visible and path is clear)
        self.ensure_forward(current_cmd, is_moving)
        self.apply_vision_steering(x)
        return "APPROACHING"

    def handle_obstacle_avoidance(self, current_cmd, is_moving):
        """State-Aware Sliding: Switches direction if the current path gets blocked."""

        # Sensor Groups
        left_blocked = self.sonar_ctrl.is_blocked("L") or self.sonar_ctrl.is_blocked("FL")
        right_blocked = self.sonar_ctrl.is_blocked("R") or self.sonar_ctrl.is_blocked("FR")
        front_blocked = self.sonar_ctrl.is_blocked("FM")

        # B. INITIAL DODGE TRIGGERS
        # If Front or Right is blocked, slide Left
        if front_blocked or right_blocked:
            if not isinstance(current_cmd, LeftCommand) or not is_moving:
                print("Dodge: Right/Front blocked. Sliding LEFT.")
                self.motor_ctrl.set_move_command(LeftCommand())
            return "DODGING_LEFT"

        # If Left is blocked, slide Right
        if left_blocked:
            if not isinstance(current_cmd, RightCommand) or not is_moving:
                print("Dodge: Left blocked. Sliding RIGHT.")
                self.motor_ctrl.set_move_command(RightCommand())
            return "DODGING_RIGHT"

        return None  # Path is clear

    def handle_target_reached(self, x, current_cmd, is_moving):
        """Final alignment and stopping logic."""
        # If x is None here, we use a large error to force alignment
        error = x - self.CENTER_POINT if x is not None else 999

        dist = self.sonar_ctrl.get_sonar_distance("FM")
        # print(f"Target Centered. Distance: {dist}cm")

        if dist < 17:
            if not isinstance(current_cmd, BackwardsCommand) or not is_moving:
                self.motor_ctrl.set_move_command(BackwardsCommand())
            return "ADJUSTING_BACK"

        if abs(error) <= self.MARGIN:
            print(self.sonar_ctrl.get_sonar_distance("FM"))
            if  self.sonar_ctrl.get_sonar_distance("FM") < 20 or  self.sonar_ctrl.get_sonar_distance("FL") < 20 or  self.sonar_ctrl.get_sonar_distance("FR") < 20:

                if not isinstance(current_cmd, BackwardsCommand) or not is_moving:
                    self.motor_ctrl.reset_all_motors_rpm()
                    self.motor_ctrl.set_move_command(BackwardsCommand())
            else:
                self.motor_ctrl.stop_movement()
            print("!!! TARGET CENTERED AND REACHED !!!")
            self.collect_cup()
            return

        sleep_time = abs(error) / 3000

        print(sleep_time)
        print(error)

        if error > 0:
            # Target is to the Right -> Pivot Right
            if not isinstance(current_cmd, ClockwiseCommand) or not is_moving:
                # Optional: You can set lower RPM for more precision
                self.motor_ctrl.set_motor_rpm("ALL", 20)
                time.sleep(0.1)
                self.motor_ctrl.set_move_command(ClockwiseCommand())
                time.sleep(sleep_time)
                self.motor_ctrl.stop_movement()
                self.motor_ctrl.reset_all_motors_rpm()
        else:
            # Target is to the Left -> Pivot Left
            # (Assuming you have a CounterClockwise or LeftPivot command)
            if not isinstance(current_cmd, CounterClockwiseCommand) or not is_moving:
                self.motor_ctrl.set_motor_rpm("ALL", 20)
                time.sleep(0.1)
                self.motor_ctrl.set_move_command(CounterClockwiseCommand())
                time.sleep(sleep_time)
                self.motor_ctrl.stop_movement()
                self.motor_ctrl.reset_all_motors_rpm()
        return "DONE"

    def handle_search(self, current_cmd, is_moving):
        """Spin to find the cup if it's lost."""
        if not isinstance(current_cmd, ClockwiseCommand) or not is_moving:
            print("Target lost. Searching...")
            self.motor_ctrl.set_move_command(ClockwiseCommand())
        return "SEARCHING"

    def ensure_forward(self, current_cmd, is_moving):
        """Maintains the ForwardsCommand state."""
        if not isinstance(current_cmd, ForwardsCommand) or not is_moving:
            self.motor_ctrl.set_move_command(ForwardsCommand())

    def apply_vision_steering(self, target_x):
        """Dynamic RPM adjustment to center the cup while moving forward."""
        error = target_x - self.CENTER_POINT

        if abs(error) <= self.MARGIN:
            self.motor_ctrl.reset_all_motors_rpm()
        elif error < 0:  # Target is to the Left
            self.motor_ctrl.set_motor_rpm("FL", self.CORRECTION_RPM)
            self.motor_ctrl.set_motor_rpm("BL", self.CORRECTION_RPM)
            self.motor_ctrl.reset_motor_rpm("FR")
            self.motor_ctrl.reset_motor_rpm("BR")
        else:  # Target is to the Right
            self.motor_ctrl.set_motor_rpm("FR", self.CORRECTION_RPM)
            self.motor_ctrl.set_motor_rpm("BR", self.CORRECTION_RPM)
            self.motor_ctrl.reset_motor_rpm("FL")
            self.motor_ctrl.reset_motor_rpm("BL")

    def collect_cup(self):
        print("Starting Collection Sequence...")

        # 1. Stop everything safely
        self.motor_ctrl.stop_movement()

        # 2. Ensure frequency is 50Hz for the Servo
        # Only set this once. If your motors are already at 50Hz, remove this line.
        self.servo_ctrl.set_pca()
        time.sleep(0.1)  # Give the chip a moment to stabilize

        print("Lowering Arm...")
        self.servo_ctrl.lower_mg996r()
        time.sleep(0.8)

        print("Driving Forward into cup...")
        self.motor_ctrl.set_move_command(ForwardsCommand())
        time.sleep(1.0)
        self.motor_ctrl.stop_movement()

        self.servo_ctrl.close_sg90()
        time.sleep(1.0)
        self.servo_ctrl.raise_mg996r()
        time.sleep(0.8)
        self.servo_ctrl.open_sg90()
        time.sleep(1.0)

        self.servo_ctrl.return_pca()
        print("Collection Complete.")