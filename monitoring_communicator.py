import socket
from decimal import Decimal
import time
import requests
UDP_IP = "192.168.0.34"
UDP_PORT = 2390
MESSAGE = "#01\r"

DB_URL = "http://127.0.0.1:5000/blindspot"


def establishUDPConnection(UDP_IP, UDP_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.settimeout(5)
    try:
        while(True):

            sock.sendto(MESSAGE.encode(encoding='utf-8'), (UDP_IP, UDP_PORT))
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print(data)
            uploadMonitoringDataToLocal(data.decode())
    except requests.Timeout as err:
        print("Timed out... reopening")
        sock.close()
        establishUDPConnection(UDP_IP, UDP_PORT)

def uploadMonitoringDataToLocal(data):
    requests.post(DB_URL, data=data)
