import cv2
import numpy as np

class VisionController:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        # Define color boundaries (Example: Bright Red)
        self.lower_color = np.array([0, 120, 70])
        self.upper_color = np.array([10, 255, 255])

    def get_target(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, 0

        # Convert to HSV and create a mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        # Find "contours" (shapes) in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest red object
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 500:  # Noise filter
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    return center_x, area

        return None, 0

    def release(self):
        self.cap.release()