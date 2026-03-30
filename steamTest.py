import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, render_template_string
import webcolors


class VisionSystem:
    def __init__(self, camera, target_hex="#FF00FF", port=5000):
        # 1. Setup Camera
        self.cam = camera
        # Force low res for speed
        self.cam.res = (640, 480)

        # 2. State Variables
        self.output_frame = None
        self.lock = threading.Lock()
        self.target_x = None
        self.target_area = 0
        self.running = True
        self.target_hex = target_hex

        # 3. Generate HSV Range from your HEX code
        self.lower_hsv, self.upper_hsv = self.hex_to_hsv_range(self.target_hex)

        # 4. Flask Setup
        self.app = Flask(__name__)
        self.port = port
        self._setup_routes()

    def hex_to_hsv_range(self, hex_code, h_tol=10, s_tol=70, v_tol=70):
        """Your specific logic to convert HEX to OpenCV HSV ranges."""
        rgb = webcolors.hex_to_rgb(hex_code)
        # OpenCV BGR format
        pixel = np.uint8([[[rgb.blue, rgb.green, rgb.red]]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]

        h, s, v = hsv[0], hsv[1], hsv[2]
        lower = np.array([max(0, h - h_tol), max(40, s - s_tol), max(40, v - v_tol)])
        upper = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])
        return lower, upper

    def _vision_loop(self):
        """High-speed background thread."""
        while self.running:
            # CAPTURE: Direct to array (No disk I/O)
            frame = self.cam.get_cam().capture_array()

            # CONVERT: RGB (PiCam) to BGR (OpenCV)
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

            # MASKING: Using your calculated HEX ranges
            mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)

            # CLEANUP: Erode/Dilate to remove noise
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            found_x, found_area = None, 0
            if contours:
                # Find the largest blob matching your color
                largest = max(contours, key=cv2.contourArea)
                found_area = cv2.contourArea(largest)

                if found_area > 500:  # Threshold to ignore tiny spots
                    M = cv2.moments(largest)
                    if M["m00"] != 0:
                        found_x = int(M["m10"] / M["m00"])
                        # Draw on the BGR frame for the Web Stream
                        cv2.drawContours(bgr_frame, [largest], -1, (0, 255, 0), 2)
                        cv2.circle(bgr_frame, (found_x, int(M["m01"] / M["m00"])), 5, (0, 0, 255), -1)

            # Thread-safe update
            with self.lock:
                self.target_x = found_x
                self.target_area = found_area
                self.output_frame = bgr_frame

    def get_data(self):
        """The robot calls this to get the latest X and Area."""
        with self.lock:
            return self.target_x, self.target_area

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string('<html><body style="background:#000; color:white; text-align:center;">'
                                          '<h1>Robot Live Feed</h1><img src="/video_feed" style="width:80%;"></body></html>')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self._generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def _generate(self):
        """Web server internal loop to stream frames."""
        while self.running:
            with self.lock:
                if self.output_frame is None:
                    continue
                ret, buffer = cv2.imencode('.jpg', self.output_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if not ret: continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)  # Cap stream at ~30FPS to save bandwidth

    def start(self):
        """Starts both the Vision Thread and the Web Server."""
        # Start Vision
        vt = threading.Thread(target=self._vision_loop)
        vt.daemon = True
        vt.start()

        # Start Web Server
        st = threading.Thread(
            target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True, use_reloader=False))
        st.daemon = True
        st.start()
        print(f"[*] Vision System Online at http://localhost:{self.port}")
