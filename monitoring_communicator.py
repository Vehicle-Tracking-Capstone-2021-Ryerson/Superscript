import socket
from decimal import Decimal
import time
import requests
import RPi.GPIO as GPIO


UDP_IP = "192.168.0.34"
UDP_PORT = 2390
MESSAGE = "#01\r"

buzzerPin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.setwarnings(False)


DB_URL = "http://127.0.0.1:5000/blindspot"


def establishUDPConnection(UDP_IP, UDP_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.settimeout(5)
    buzzTime = time.time_ns()
    try:
        while(True):

            sock.sendto(MESSAGE.encode(encoding='utf-8'), (UDP_IP, UDP_PORT))
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            # print(data)
            incomingBSM = data.decode()
            whichOne, dist = incomingBSM.split(",")
            
            if(time.time_ns() - buzzTime > 500000000):
                GPIO.output(buzzerPin, GPIO.LOW)

            if whichOne == "B":
                    print(whichOne + " " + str(dist))

            if(whichOne == "L" or whichOne == "R"):
                #print(time.time_ns() - buzzTime)
                if(int(dist) < 100 and time.time_ns() - buzzTime > 5e+9 ):
                    GPIO.output(buzzerPin, GPIO.HIGH)
                    buzzTime = time.time_ns()
                if(time.time_ns() - buzzTime > 1e+9):
                    GPIO.output(buzzerPin, GPIO.LOW)
            


            uploadMonitoringDataToLocal(data.decode())
    except socket.timeout as err:
        print("Timed out... reopening")
        sock.close()
    establishUDPConnection(UDP_IP, UDP_PORT)

def uploadMonitoringDataToLocal(data):
    requests.post(DB_URL, data=data)
