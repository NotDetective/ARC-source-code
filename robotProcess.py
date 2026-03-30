import time
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand

class RobotProcess:
    def __init__(self, motor, model_ctrl, color_ctrl, sonar_ctrl, vision, target_hex, model, timeout=40.0):
        self.motor_ctrl = motor
        self.model_ctrl = model_ctrl
        self.color_ctrl = color_ctrl
        self.sonar_ctrl = sonar_ctrl
        self.vision = vision
        self.target_hex = target_hex
        self.model = model

        # Constants
        self.IMG_WIDTH = 4608
        self.CENTER_POINT = self.IMG_WIDTH // 2
        self.DEADZONE = 150  # Margin for centering
        self.TARGET_SIZE_THRESHOLD = 250000  # When to stop/collect
        self.SCAN_SPEED_RPM = 50

    def run_robot_process(self):
        """
        Main execution loop. Call this inside a 'while True' in your main script.
        """
        # 1. Get live data
        x, size = self.vision.get_data()

        # 2. Logic: What do I see?

        # SCENARIO A: Target is not in sight
        if x is None:
            print("Target lost: Scanning...")
            if not isinstance(self.motor_ctrl.get_current_command(), ClockwiseCommand) and not self.motor_ctrl.has_active_command():
                self.motor_ctrl.set_move_command(ClockwiseCommand())
            return "SEARCHING"

        # SCENARIO B: Target is reached (Close enough)
        if size > self.TARGET_SIZE_THRESHOLD:
            print("Target reached! Stopping.")
            self.motor_ctrl.stop_movement()
            return "ARRIVED"

        # SCENARIO C: Target is in sight, move toward it with steering
        self.execute_proportional_drive(x)
        return "APPROACHING"

    def execute_proportional_drive(self, target_x):
        """
        Adjusts motor speeds on the fly to center the target while moving forward.
        """

        if not isinstance(self.motor_ctrl.get_current_command(), ForwardsCommand):
            self.motor_ctrl.set_move_command(ForwardsCommand())

        error = target_x - self.CENTER_POINT

        # If centered within deadzone, full speed ahead
        if abs(error) <= self.DEADZONE:
            self.motor_ctrl.reset_all_motors_rpm()
            print(f"Centered: Moving Straight (Error: {error:.2f})")

        # If target is to the Left, slow down Left motors to pivot left
        elif error < 0:
            self.motor_ctrl.reset_motor_rpm("FR")
            self.motor_ctrl.reset_motor_rpm("BR")
            self.motor_ctrl.set_motor_rpm("FL", 40)
            self.motor_ctrl.set_motor_rpm("BL", 40)
            print(f"Adjusting LEFT (Error: {error:.2f})")

        # If target is to the Right, slow down Right motors to pivot right
        else:
            self.motor_ctrl.reset_motor_rpm("FL")
            self.motor_ctrl.reset_motor_rpm("BL")
            self.motor_ctrl.set_motor_rpm("FR", 40)
            self.motor_ctrl.set_motor_rpm("BR", 40)
            print(f"Adjusting RIGHT (Error: {error:.2f})")


