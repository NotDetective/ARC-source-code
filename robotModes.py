# agline with cup and collect.
def agline_and_collect():
    pass while True:
        image = cam.take_foto("agline")
        results = model_controller.get_detected_cups(trained_model, image)
        box_data = model_controller.get_biggest_box_boundaries(results)
        all_color_blobs = color_controller.find_hex_object(image, TARGET_HEX)

        target_x = None

        if box_data and all_color_blobs:
            x1, y1, x2, y2 = box_data
            filtered_blobs = [ (bx, by) for (bx, by) in all_color_blobs if x1 <= bx <= x2 and y1 <= by <= y2 ]
            
            if filtered_blobs:
                target_x = sum(b[0] for b in filtered_blobs) / len(filtered_blobs)

        if target_x is not None:
            screen_center = IMAGE_WIDTH / 2
            error = target_x - screen_center

            if abs(error) <= CENTER_THRESHOLD:
                print("Target Centered! Moving Forward...")
                # motorController.give_move_command(ForwardsCommand(), 100)
            elif error > 0:
                print(f"Target is Right (error: {error}). Turning Right...")
                motor_controller.give_move_command(RightCommand(), int(error/50))
            else:
                print(f"Target is Left (error: {error}). Turning Left...")
                motor_controller.give_move_command(LeftCommand(), int((error * -1) /50)  )
        else:
            print("Searching for cup...")

        time.sleep(0.1) 

def agline_with_cup():
    pass

def collect_cup():
    pass

# find target to go to
def find():
     while True:        
        image = cam.take_foto("find-cup")
        results = model_controller.get_detected_cups(trained_model, image)    
        if not model_controller.has_detected_cups(results):
            print("end")
            break
        else:
            motor_controller.give_move_command(ClockwiseCommand(), get_rotation_steps(45))
            
            
def scan():
    while True:
        print(current_state)
        image_path = cam.take_photo("scan") 
        
        results = model_controller.get_detected_cups(trained_model, image_path)
        
        cup_found = not model_controller.has_detected_cups(results)

        if current_state == "SCAN":
            if cup_found:
                motor_controller.stop_movement()
                print("Cup detected! Transitioning to GO.")
                current_state = "GO"
                scan_start_time = None
                
                raise Exception("done")
                
            else:
                if scan_start_time is None:
                    print("No cup in sight. Starting slow rotation scan...")
                    scan_start_time = time.time()
                    
                    print(motor_controller.has_active_command())
                    
                    if not motor_controller.has_active_command():
                        motor_controller.set_move_command(ClockwiseCommand()) 
                
                if time.time() - scan_start_time > SCAN_TIMEOUT:
                    print("360 degree scan failed to find cup. Switching to SEARCH.")
                    motor_controller.stop_movement()
                    scan_start_time = None
                    current_state = "SEARCH"
        time.sleep(0.05)

# drive to target 
def drive():
    pass