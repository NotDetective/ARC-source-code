import serial
import struct
import threading
import time
from flask import Flask, jsonify, render_template_string

PORT = "/dev/ttyUSB0"
BAUD = 128000

ser = serial.Serial(PORT, BAUD, timeout=1)

app = Flask(__name__)

# Shared lidar data
lidar_points = []

def read_lidar():
    global lidar_points

    while True:
        header = ser.read(2)
        if header != b'\xaa\x55':
            continue

        type_quality = ser.read(2)
        length = type_quality[1]

        fsa_raw = struct.unpack('<H', ser.read(2))[0]
        lsa_raw = struct.unpack('<H', ser.read(2))[0]
        cs = ser.read(2)

        fsa = (fsa_raw >> 1) / 64.0
        lsa = (lsa_raw >> 1) / 64.0
        diff = (lsa - fsa) % 360

        raw_dist = ser.read(length * 2)

        new_points = []

        for i in range(length):
            dist_bytes = raw_dist[i*2 : (i+1)*2]
            distance = struct.unpack('<H', dist_bytes)[0] / 4.0

            if distance > 0:
                angle_step = diff / max(1, length - 1)
                angle = (angle_step * i + fsa) % 360
                new_points.append((angle, distance))

        lidar_points = new_points


@app.route("/data")
def data():
    return jsonify(lidar_points)


@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Lidar Live Map</title>
</head>
<body>
<canvas id="lidarCanvas" width="600" height="600"></canvas>

<script>
const canvas = document.getElementById("lidarCanvas");
const ctx = canvas.getContext("2d");
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;

function draw(points) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "lime";

    points.forEach(p => {
        const angle = p[0] * Math.PI / 180;
        const distance = p[1] / 5;  // scale down

        const x = centerX + distance * Math.cos(angle);
        const y = centerY + distance * Math.sin(angle);

        ctx.fillRect(x, y, 2, 2);
    });
}

async function update() {
    const response = await fetch("/data");
    const points = await response.json();
    draw(points);
}

setInterval(update, 100);
</script>
</body>
</html>
    """)

if __name__ == "__main__":
    t = threading.Thread(target=read_lidar)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=5000)