import time
from moveCommands.forwardsCommand import ForwardsCommand
from moveCommands.leftCommand import LeftCommand
from moveCommands.rightCommand import RightCommand
from moveCommands.clockwiseCommand import ClockwiseCommand

class RobotProcess:
    def __init__(self, motor, model_ctrl, color_ctrl, sonar_ctrl, camera, target_hex, model, timeout=40.0):
        self.motor = motor
        self.model_ctrl = model_ctrl
        self.color_ctrl = color_ctrl
        self.sonar_ctrl = sonar_ctrl
        self.cam = camera
        self.target_hex = target_hex
        self.model = model 
        
        self.scan_timeout = timeout
        self.current_state = "ALGIN"
        self.scan_start_time = None
        
        # Constants
        self.IMG_WIDTH = 4608
        self.MARGIN = 150 
        self.CENTER_POINT = self.IMG_WIDTH // 2

    def run_state_logic(self):
        print(f"--- State: {self.current_state} ---")
        match self.current_state:
            case "SCAN":   return self.run_scan_logic()
            case "SEARCH": return self.run_search_logic()
            case "GO":     return self.run_go_logic()
            case "ALIGN":  return self.run_align_logic()
        return "CONTINUE"

    def _get_target_x(self, image_path):
        """Helper to combine Model detection and Color filtering."""
        results = self.model_ctrl.get_detected_cups(self.model, image_path)
        box_data = self.model_ctrl.get_biggest_box_boundaries(results)
        all_blobs = self.color_ctrl.find_hex_object(image_path, self.target_hex)

        if box_data and all_blobs:
            x1, y1, x2, y2 = box_data
            filtered = [b for b in all_blobs if x1 <= b[0] <= x2 and y1 <= b[1] <= y2]
            if filtered:
                avg_x = sum(b[0] for b in filtered) / len(filtered)
                return avg_x, filtered[0][2] 
        return None, 0

    def run_scan_logic(self):
        self.motor.stop_movement()
        image_path = self.cam.take_photo("scan") 
        target_x, _ = self._get_target_x(image_path)
        
        if target_x is not None:
            print(f"Target locked at X:{target_x}. Switching to GO.")
            self.current_state = "GO"
            self.scan_start_time = None
            return "FOUND" 
        
        if self.scan_start_time is None:
            self.scan_start_time = time.time()
        
        self.motor.set_move_command(ClockwiseCommand()) 
        if time.time() - self.scan_start_time > self.scan_timeout:
            self.current_state = "SEARCH"
        
        time.sleep(1)
        return "CONTINUE"

    def run_go_logic(self):
        image_path = self.cam.take_photo("approach")
        target_x, blob_area = self._get_target_x(image_path)

        if target_x is None:
            print("Target lost! Reverting to SCAN.")
            self.motor.stop_movement()
            self.current_state = "SCAN"
            return "CONTINUE"

        if blob_area > 250000: 
            print("Target reached. Transitioning to ALIGN.")
            self.motor.stop_movement()
            self.current_state = "ALIGN"
            return "CONTINUE"

        if not self.motor.has_active_command():
            self.motor.set_move_command(ForwardsCommand())

        error = target_x - self.CENTER_POINT
        
        if abs(error) <= self.MARGIN:
            print(f"Centered! Moving Straight (Error: {error:.2f})")
            self.motor.reset_all_motors_rpm()
        elif error < 0:
            print(f"Steering LEFT (Error: {error:.2f})")
            self.motor.reset_motor_rpm("FR")
            self.motor.reset_motor_rpm("BR")
            self.motor.set_motor_rpm("FL", 50) # Slow down inside wheel
            self.motor.set_motor_rpm("BL", 50)
        else:
            print(f"Steering RIGHT (Error: {error:.2f})")
            self.motor.reset_motor_rpm("FL")
            self.motor.reset_motor_rpm("BL")
            self.motor.set_motor_rpm("FR", 50) # Slow down inside wheel
            self.motor.set_motor_rpm("BR", 50)
        
        return "CONTINUE"

    def run_search_logic(self):
        print("Moving to a new area...")
        self.motor.set_move_command(ForwardsCommand())
        time.sleep(2.0)
        self.current_state = "SCAN"
        return "CONTINUE"
    
    def run_align_logic(self):
        image = self.cam.take_photo("align")
        results = self.model_ctrl.get_detected_cups(self.model, image) 
        box_data = self.model_ctrl.get_biggest_box_boundaries(results)
        all_color_blobs = self.color_ctrl.find_hex_object(image, self.target_hex)

        target_x = None

        if box_data and all_color_blobs:
            x1, y1, x2, y2 = box_data
            
            filtered_blobs = [(bx, by) for (bx, by, _) in all_color_blobs 
                            if x1 <= bx <= x2 and y1 <= by <= y2]
            
            if filtered_blobs:
                target_x = sum(b[0] for b in filtered_blobs) / len(filtered_blobs)

        if target_x is not None:
            error = target_x - self.CENTER_POINT

            if abs(error) <= self.MARGIN:
                print("Target Centered! Moving to COLLECT...")
                self.motor.stop_movement()
                self.current_state = "COLLECT"
            elif error > 0:
                print(f"Target is Right (error: {error}). Turning Right...")
                self.motor.set_move_command(RightCommand())
                time.sleep(abs(error)/900) 
                self.motor.stop_movement()
            else:
                print(f"Target is Left (error: {error}). Turning Left...")
                self.motor.set_move_command(LeftCommand())
                time.sleep(abs(error)/900)
                self.motor.stop_movement()
        else:
            print("Searching for cup...")

        return "CONTINUE"