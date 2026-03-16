import serial
import time
import struct
import matplotlib.pyplot as plt
import numpy as np

# Configuration
PORT = "/dev/ttyUSB0"
BAUD = 128000 

x = np.linspace(0, 2 * np.pi, 200)

ser = serial.Serial(PORT, BAUD, timeout=1) # open the serial port

while True:
    # check for start bit
    header = ser.read(2)
    if header != b'\xaa\x55': # if it is not a the starting bits
        continue

    # read the paclet info
    type_quality = ser.read(2) # read the Package type and Sample Quality
    length = type_quality[1] # package length in integer

    # convert the 2 bytes to an unsgned short integer
    fsa_raw = struct.unpack('<H', ser.read(2))[0] # read the FSA (First Sample Angle)
    lsa_raw = struct.unpack('<H', ser.read(2))[0] # read the LSA (Last Sample Angle)
    cs = ser.read(2) # read the Checksum

    fsa = (fsa_raw >> 1) / 64.0 # convert FSA to degrees
    lsa = (lsa_raw >> 1) / 64.0 # convert LSA to degrees
    diff = (lsa - fsa) % 360 # the angle difference

    raw_dist = ser.read(length * 2) # read the distance bytes

    for i in range(length):
        dist_bytes = raw_dist[i*2 : (i+1)*2] # get the 2 bytes for the distance
        distance = struct.unpack('<H', dist_bytes)[0] / 4.0 # convert the data to millimeters

        if distance > 0: 
            angle_step = diff / max(1, length - 1) # calculate the angle step between points and prevent division by zero
            angle = (angle_step * i + fsa) % 360 # fill the blanks for all the points in between
            print(f"Angle: {angle:6.2f} degrees, Distance: {distance:8.2f} mm") # print the angle and distance