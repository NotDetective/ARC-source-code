from camera.camera import MyCamera
import cv2
import os

class ModelController:
    
    def get_detected_cups(self, model, picture):
        results = model(picture)
        self.__draw_detected_cups(results, picture)
        return results 

    def __draw_detected_cups(self, results, picture):
        img = results[0].orig_img.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2          
        font_thickness = 3       
        padding = 10
        border = 8
        color = ( 103, 31, ) #(b,g,r)
        text_color = (255, 255, 255)

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, border) # Thicker box border

            conf_score = float(box.conf[0])
            label_text = f"Cup {conf_score:.2f}"

            (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
            
            bg_rect_x1 = x1
            bg_rect_y1 = y1 - th - (padding * 2)
            bg_rect_x2 = x1 + tw + (padding * 2)
            bg_rect_y2 = y1
            
            cv2.rectangle(img, (bg_rect_x1, bg_rect_y1), (bg_rect_x2, bg_rect_y2), color, -1)

            text_x = x1 + padding
            text_y = y1 - padding
            cv2.putText(img, label_text, (text_x, text_y), font, font_scale, text_color, font_thickness, lineType=cv2.LINE_AA)
        
        filename = os.path.basename(picture)
        save_dir = "images"
        save_path = os.path.join(save_dir, f"boxed-{filename}")

        success = cv2.imwrite(save_path, img)
        
        if success:
            print(f"Successfully saved to {save_path}")
        else:
            print("Failed to save image. Check file permissions or path.")
        
    
    def has_detected_cups(self, results):
        boxes = results[0].boxes
        return len(boxes) == 0
            
    def get_angle_of_cups(self, model, picture):
        
        HFOV = MyCamera().get_FOV()  
                
        results = self.get_detected_cups(model, picture)
        
        if self.has_detected_cups(results):
            print("No objects detected at all.")
            return
        
        img_width = results[0].orig_shape[1]
        img_center_x = img_width / 2

        boxes = results[0].boxes
            
        closest_box = min(boxes, key=lambda x: abs(x.xywh[0][0] - img_center_x))

        class_id = int(closest_box.cls[0])
        label = model.names[class_id]

        cup_center_x = closest_box.xywh[0][0].item()
        pixel_offset = cup_center_x - img_center_x
        degree_offset = pixel_offset * (HFOV / img_width)

        print(f"Target: {label}")
        print(f"Center Offset: {pixel_offset:.1f} pixels")
        print(f"Degrees from Middle: {degree_offset:.2f}°")


        
    def open_camera_feed(self, model):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            results = model(frame)

            annotated_frame = results[0].plot()

            cv2.imshow("YOLO Live Detection", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        
    def get_biggest_box_boundaries(self, results):
        if self.has_detected_cups(results):
            return None
        
        boxes = results[0].boxes
        biggest_box = max(boxes, key=lambda b: b.xywh[0][2] * b.xywh[0][3])
        
        return map(int, biggest_box.xyxy[0].tolist())