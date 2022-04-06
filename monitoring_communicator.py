import socket
import time
import requests
from playsound import playsound


UDP_IP = "192.168.0.34"
UDP_PORT = 2390
MESSAGE = "#01\r"


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

            if whichOne == "B":
                    print(whichOne + " " + str(dist))

            if(whichOne == "L" or whichOne == "R"):
                #print(time.time_ns() - buzzTime)
                if(int(dist) < 100 and int(dist) != 0 and time.time_ns() - buzzTime > 2e+10 ):
                    if(whichOne == "L"):
                        playsound("Sounds/left_warning.mp3", block=False)
                    else:
                        playsound("Sounds/right_warning.mp3", block=False)
                    buzzTime = time.time_ns()

            uploadMonitoringDataToLocal(data.decode())
    except socket.timeout as err:
        print("Timed out... reopening")
        sock.close()
    establishUDPConnection(UDP_IP, UDP_PORT)

def uploadMonitoringDataToLocal(data):
    requests.post(DB_URL, data=data)
