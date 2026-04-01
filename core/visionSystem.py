import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, render_template_string
import webcolors


class VisionSystem:
    def __init__(self, camera, target_hex="#FF00FF", port=5000, line_y=1200):
        # 1. Setup Camera
        self.cam = camera

        # 2. State Variables
        self.output_frame = None
        self.lock = threading.Lock()
        self.target_x = None
        self.target_area = 0
        self.running = True
        self.target_hex = target_hex

        # 3. Line threshold (blobs must be below this Y coordinate)
        self.line_y = line_y

        # 4. Generate HSV Range
        self.lower_hsv, self.upper_hsv = self.hex_to_hsv_range(self.target_hex)

        # 5. Flask Setup
        self.app = Flask(__name__)
        self.port = port
        self._setup_routes()

    def hex_to_hsv_range(self, hex_code, h_tol=10, s_tol=70, v_tol=70):
        rgb = webcolors.hex_to_rgb(hex_code)
        pixel = np.uint8([[[rgb.blue, rgb.green, rgb.red]]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = hsv[0], hsv[1], hsv[2]
        lower = np.array([max(0, h - h_tol), max(40, s - s_tol), max(40, v - v_tol)])
        upper = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])
        return lower, upper

    def _vision_loop(self):
        """High-speed background thread with ROI filtering."""
        while self.running:
            frame = self.cam.get_cam().capture_array()
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # --- 1. Draw the ROI Line on the display frame ---
            # Arguments: (image, start_point, end_point, color_bgr, thickness)
            height, width = bgr_frame.shape[:2]
            cv2.line(bgr_frame, (0, self.line_y), (width, self.line_y), (255, 0, 0), 2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            found_x, found_area = None, 0

            if contours:
                valid_blobs = []
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > 500:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])

                            # --- 2. Check if the blob is BELOW the line ---
                            if cy > self.line_y:
                                valid_blobs.append((cnt, area, cx, cy))

                if valid_blobs:
                    # Pick the largest blob that passed the height test
                    largest_cnt, area, cx, cy = max(valid_blobs, key=lambda x: x[1])

                    found_x = cx
                    found_area = area

                    # Draw detection visuals for the web feed
                    cv2.drawContours(bgr_frame, [largest_cnt], -1, (0, 255, 0), 2)
                    cv2.circle(bgr_frame, (cx, cy), 5, (0, 0, 255), -1)

            with self.lock:
                self.target_x = found_x
                self.target_area = found_area
                self.output_frame = bgr_frame

    def get_data(self):
        with self.lock:
            return self.target_x, self.target_area

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string('<html><body style="background:#000; color:white; text-align:center;">'
                                          '<h1>Robot Live Feed</h1>'
                                          '<p>Detection only active BELOW the blue line</p>'
                                          '<img src="/video_feed" style="width:80%;"></body></html>')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self._generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def _generate(self):
        while self.running:
            with self.lock:
                if self.output_frame is None:
                    continue
                ret, buffer = cv2.imencode('.jpg', self.output_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if not ret: continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)

    def start(self):
        vt = threading.Thread(target=self._vision_loop)
        vt.daemon = True
        vt.start()

        st = threading.Thread(
            target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True, use_reloader=False))
        st.daemon = True
        st.start()
        print(f"[*] Vision System Online at http://localhost:{self.port}")