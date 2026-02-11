from camera.camera import MyCamera as Camera
from motor.motor import Motor

cam = Camera()
cam.start_camera()

test = Motor(None, isInInverted=True)
test2 = Motor(None, isInInverted=False)

print(test.set_speed(-0.1))    
print(test2.set_speed(-0.1))

# while True: 
#     pass