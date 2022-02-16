import socket
import csv
import datetime
from decimal import Decimal
import time

UDP_IP = "192.168.0.34"
UDP_PORT = 2390
MESSAGE = "#01\r"


def establishUDPConnection(UDP_IP, UDP_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    while(True):

        sock.sendto(MESSAGE.encode(encoding='utf-8'), (UDP_IP, UDP_PORT))

        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message:", str(data))
