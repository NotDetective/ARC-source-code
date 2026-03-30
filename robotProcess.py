import time
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand

class RobotProcess:
    def __init__(self, motor_ctrl, model_ctrl, color_ctrl, sonar_ctrl, vision, target_hex, model, timeout=40.0):
        self.motor_ctrl = motor_ctrl
        self.model_ctrl = model_ctrl
        self.color_ctrl = color_ctrl
        self.sonar_ctrl = sonar_ctrl
        self.vision = vision
        self.target_hex = target_hex
        self.model = model

        # Constants
        self.IMG_WIDTH = 4608
        self.CENTER_POINT = self.IMG_WIDTH // 2
        self.MARGIN = 150
        self.GOAL_SIZE = 250000

    def run_robot_process(self):
        # 1. Gather all "Senses"
        current_cmd = self.motor_ctrl.get_current_command()
        is_moving = self.motor_ctrl.has_active_command()

        if self.sonar_ctrl.is_blocked("FM") or self.sonar_ctrl.is_blocked("FR"):
            if not isinstance(current_cmd, LeftCommand) or not is_moving:
                print("!!! Obstacle Right/Center: Sliding LEFT !!!")
                self.motor_ctrl.set_move_command(LeftCommand())
            return "AVOIDING_LEFT"

        # If something is in front-left, SLIDE RIGHT
        if self.sonar_ctrl.is_blocked("FL"):
            if not isinstance(current_cmd, RightCommand) or not is_moving:
                print("!!! Obstacle Left: Sliding RIGHT !!!")
                self.motor_ctrl.set_move_command(RightCommand())
            return "AVOIDING_RIGHT"

        x, size = self.vision.get_data()

        # 3. Priority 2: Target Tracking (Vision)
        if x is None:
            # Not using isinstance(ClockwiseCommand) here because if we are 
            # arcing around an obstacle, we don't want to suddenly spin.
            if not isinstance(current_cmd, ClockwiseCommand) or not is_moving:
                self.motor_ctrl.set_move_command(ClockwiseCommand())
            return

        if size > self.GOAL_SIZE:
            print("Target Reached.")
            self.motor_ctrl.stop_movement()
            return

        # Normal vision-based steering
        self.ensure_forward(current_cmd, is_moving)
        self.apply_vision_steering(x)

    def ensure_forward(self, current_cmd, is_moving):
        """Maintains the ForwardsCommand state using isinstance."""
        if not isinstance(current_cmd, ForwardsCommand) or not is_moving:
            self.motor_ctrl.set_move_command(ForwardsCommand())

    def apply_vision_steering(self, target_x):
        error = target_x - self.CENTER_POINT
        if abs(error) <= self.MARGIN:
            self.motor_ctrl.reset_all_motors_rpm()
        elif error < 0:  # Target is to the Left
            self.motor_ctrl.set_motor_rpm("FL", 50)
            self.motor_ctrl.set_motor_rpm("BL", 50)
            self.motor_ctrl.set_motor_rpm("FR")
            self.motor_ctrl.set_motor_rpm("BR")
        else:  # Target is to the Right
            self.motor_ctrl.set_motor_rpm("FR", 50)
            self.motor_ctrl.set_motor_rpm("BR", 50)
            self.motor_ctrl.set_motor_rpm("FL")
            self.motor_ctrl.set_motor_rpm("BL")


