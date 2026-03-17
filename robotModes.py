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

# drive to target 
def drive():
    pass