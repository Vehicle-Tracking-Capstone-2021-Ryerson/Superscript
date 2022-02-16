from picamera import PiCamera
from time import sleep
import os


class camStuff:
    def __init__(self):
        self.camera = PiCamera()
        self.shouldDelete = True

    def setShouldDelete(self, bool):
        self.shouldDelete = bool

    def deleteVideo():
        print("Deleting video")
        os.remove('/home/pi/Desktop/camera/video.h264')

    def captureTime(self):
        self.camera.resolution = (1920, 1080)
        while(self.camera):
            self.camera.start_recording('/home/pi/Desktop/camera/video.h264')
            print("Started recording new video...\n")
            sleep(600)
            print("Stopping recording...\n")
            self.camera.stop_recording()
            if(self.shouldDelete):
                self.deleteVideo()
