from picamera import PiCamera 
from time import sleep
import os

camera = PiCamera()

shouldDelete = True


    

def captureTime():
    camera.resolution = (1920,1080)
    camera.start_recording('/home/pi/Desktop/camera/video.h264')
    print("Started recording new video...\n")
    sleep(600)
    print("Stopping recording...\n")
    camera.stop_recording()
    if(shouldDelete):
        deleteVideo()
    
def deleteVideo():
    print("Deleting video")
    os.remove('/home/pi/Desktop/camera/video.h264')

while(True):
    captureTime()