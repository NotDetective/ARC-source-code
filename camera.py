import cv2
import numpy as np
import webcolors
from picamzero import Camera
from PIL import Image, ImageDraw

def hex_to_hsv_range(hex_code, tolerance=20):
    rgb = webcolors.hex_to_rgb(hex_code)
    
    bgr = np.uint8([[[rgb.blue, rgb.green, rgb.red]]])
    hsv_color = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0][0]
    
    lower = np.array([max(0, hsv_color[0] - 10), 50, 50])
    upper = np.array([min(179, hsv_color[0] + 10), 255, 255])
    
    return lower, upper

def find_hex_object(image, hex_code):
    lower, upper = hex_to_hsv_range(hex_code)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        largest_contour = sorted_contours[0]

        if cv2.contourArea(largest_contour) > 50:
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                return cX

    return None

def draw_square(img_file, middle_pos, length):
    img = Image.open(img_file) 
    
    draw = ImageDraw.Draw(img)

    draw.line(
        xy=(middle_pos, 0, middle_pos, length), 
        fill=(0, 255, 255),
        width=10
    )

    img.save(FILE_NAME)

TARGET_HEX = "#b43384"
FILE_NAME = "detect.jpg"

cam = Camera()
cam.flip_camera(vflip=True, hflip=True)
cam.take_photo(FILE_NAME)
img = cv2.imread(FILE_NAME)

x_pos = find_hex_object(img, TARGET_HEX)

if x_pos:
    width = img.shape[1]
    height = img.shape[0]
    center_threshold = 50

    draw_square("detect.jpg", x_pos, height)

    if x_pos < (width // 2) - center_threshold:
        print(f"Target at {x_pos}: Rotate Left")
    elif x_pos > (width // 2) + center_threshold:
        print(f"Target at {x_pos}: Rotate Right")
    else:
        print("Target Centered!")
else:
    print("Color not found.")