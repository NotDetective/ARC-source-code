import time
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand
from moveCommands.counterClockwiseCommand import CounterClockwiseCommand

class RobotProcess:
    def __init__(self, motor, model_ctrl, color_ctrl, sonar_ctrl, camera, target_hex, timeout=40.0):
        self.motor = motor
        self.model_ctrl = model_ctrl
        self.color_ctrl = color_ctrl
        self.sonar_ctrl = sonar_ctrl # Added sonar here
        self.cam = camera
        self.target_hex = target_hex
        self.scan_timeout = timeout
        
        self.current_state = "SCAN"
        self.scan_start_time = None
        
    def run_state_logic(self):
        print(f"Current State: {self.current_state}")
        match self.current_state:
            case "SCAN":
                return self.run_scan_logic()
            case "SEARCH":
                return self.run_search_logic()
            case "GO":
                return self.run_go_logic()
    
    def run_scan_logic(self):
        self.motor.stop_movement()
        time.sleep(0.1) 
        
        image_path = self.cam.take_photo("scan") 
        detected_blobs = self.color_ctrl.find_hex_object(image_path, self.target_hex)
        
        if detected_blobs:
            print(f"Target {self.target_hex} spotted! Switching to GO.")
            self.current_state = "GO"
            self.scan_start_time = None
            return "FOUND" 
        else:
            if self.scan_start_time is None:
                self.scan_start_time = time.time()
            
            self.motor.set_move_command(ClockwiseCommand()) 
            
            if time.time() - self.scan_start_time > self.scan_timeout:
                self.current_state = "SEARCH"
        
        time.sleep(1.5)
        return "CONTINUE"

    def run_go_logic(self):
        """Logic to approach the cup using X-coordinate and Sonar."""
        image_path = self.cam.take_photo("approach")
        detected_blobs = self.color_ctrl.find_hex_object(image_path, self.target_hex)

        if not detected_blobs:
            print("Target lost! Reverting to SCAN.")
            self.motor.stop_movement()
            self.current_state = "SCAN"
            return "CONTINUE"

        # target is (cX, cY) from your ColorController
        target = detected_blobs[0] 
        cX = target[0]  
        
        img_width = 640 
        deadzone = 60 

        self.motor.set_move_command(ForwardsCommand())

        time.sleep(0.1)
        return "CONTINUE"

    def run_search_logic(self):
        print("SEARCHING: Moving to new area...")
        self.motor.set_move_command(ForwardsCommand())
        time.sleep(2.0)
        self.current_state = "SCAN"
        return "CONTINUE"