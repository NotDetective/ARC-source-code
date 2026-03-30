import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, render_template_string
from picamzero import Camera


class VisionSystem:
    def __init__(self, camera, port=5000):
        # 1. Setup Camera
        self.cam = camera
        self.cam.res = (640, 480)

        # 2. State Variables
        self.output_frame = None
        self.lock = threading.Lock()
        self.target_x = None
        self.target_area = 0
        self.running = True

        # 3. HSV Ranges (Magenta)
        self.lower_magenta = np.array([140, 70, 70])
        self.upper_magenta = np.array([175, 255, 255])

        # 4. Flask Setup
        self.app = Flask(__name__)
        self.port = port
        self._setup_routes()

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

    def _vision_loop(self):
        """Background thread: Camera -> Math -> Draw."""
        while self.running:
            # Grab raw RGB frame
            frame = self.cam.get_cam().capture_array()

            # Convert to BGR for the Web/OpenCV (No blue filter!)
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Tracking Logic
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, self.lower_magenta, self.upper_magenta)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            found_x, found_area = None, 0
            if contours:
                largest = max(contours, key=cv2.contourArea)
                found_area = cv2.contourArea(largest)
                if found_area > 500:
                    M = cv2.moments(largest)
                    if M["m00"] != 0:
                        found_x = int(M["m10"] / M["m00"])
                        # Draw visuals for the web stream
                        cv2.drawContours(bgr_frame, [largest], -1, (0, 255, 0), 2)
                        cv2.circle(bgr_frame, (found_x, int(M["m01"] / M["m00"])), 5, (255, 255, 255), -1)

            # Update public variables for the main script
            with self.lock:
                self.target_x = found_x
                self.target_area = found_area
                self.output_frame = bgr_frame

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

    def get_data(self):
        """Returns the latest target data to your main loop."""
        return self.target_x, self.target_area