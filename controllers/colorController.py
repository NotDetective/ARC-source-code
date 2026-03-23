import cv2
import numpy as np
import webcolors
import os

class ColorController:
    
    def hex_to_hsv_range(self, hex_code, h_tol=10, s_tol=70, v_tol=70):
        rgb = webcolors.hex_to_rgb(hex_code)
        
        pixel = np.uint8([[[rgb.blue, rgb.green, rgb.red]]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
        
        h, s, v = hsv[0], hsv[1], hsv[2]

        lower = np.array([
            max(0, h - h_tol), 
            max(40, s - s_tol),
            max(40, v - v_tol)  
        ])
        
        upper = np.array([
            min(179, h + h_tol), 
            min(255, s + s_tol), 
            min(255, v + v_tol)
        ])
        
        return lower, upper
    
    def find_hex_object(self, image_input, hex_code):        
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                print(f"Error: Could not load image from path: {image_input}")
                return []
        else:
            image = image_input.copy() 

        lower, upper = self.hex_to_hsv_range(hex_code)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        
        mask = cv2.erode(mask, None, iterations=5)
        mask = cv2.dilate(mask, None, iterations=5)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_blobs = []

        if contours:
            for cnt in contours:
                if cv2.contourArea(cnt) > 100:
                    cv2.drawContours(image, [cnt], -1, (0, 255, 0), 3)
                    
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        
                        detected_blobs.append((cX, cY, cv2.contourArea(cnt)))
                        
                        cv2.circle(image, (cX, cY), 7, (0, 0, 255), -1)

            if detected_blobs:
                save_dir = "images"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                clean_hex = hex_code.replace('#','')
                save_path = os.path.join(save_dir, f"all_blobs_{clean_hex}.jpg")
                cv2.imwrite(save_path, image)
                print(f"✅ Saved {len(detected_blobs)} blobs to: {save_path}")

        return detected_blobs
    