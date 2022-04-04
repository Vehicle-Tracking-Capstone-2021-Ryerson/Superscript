import time
import json
from urllib import response
from monitoring_communicator import establishUDPConnection
# import recording
import threading
import multiprocessing as mp
import gps
import requests
import serial

# API_URL = "http://localhost:8080/"
API_URL = "https://vehicle-tracking-capstone-2021.ue.r.appspot.com/"

# cameraModule = recording.camStuff()

# ====================== BLINDSPOT MONITORING VARIABLES ======================
UDP_IPs = ["192.168.43.46", "192.168.43.170", "192.168.43.192", "192.168.43.153"] # UDP IPs for blindspot monitoring sensors
UDP_PORT = 2390 # UDP Port for blindspot monitoring sensors
monitoring_threads = [] # Array of blindspot monitoring threads
# ============================================================================

# ====================== OBD II SERIAL VARIABLES =============================
serial_str = "/dev/ttyACM0"
baudRate = 115200
# ============================================================================

DB_URL = "http://127.0.0.1:5000/" # Local Database URL

uid = -1



def uploadMonitoringDataToLocal(data, endpoint):
    requests.post(DB_URL+endpoint, data=data)

"""
GPS Functionality

Starts the gps listener on a given port and then generates gps reports that records and uploads data to listening serer
"""
def doGPS():
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    last_gps_location = 0
    last_appended = time.time()
    dataStr = ""
    while True:
        try:
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            # print(report)
            if report['class'] == 'TPV':
                lat = report['lat']
                lon = report['lon']
                dataStr = f"{lat},{lon}"
                if(time.time() - last_gps_location > 30 or last_gps_location == 0):
                    last_gps_location = time.time()
                    payload = {"location_data": dataStr}
                    response = requests.get(API_URL+"speedLimit", params=payload)

                    respData = response.json()[0]
                    street = respData["street"]
                    speed = str(respData["speedLimit"]) + respData["speedUnit"]
                    telemetryStr = f"{lat},{lon},{street},{speed}"
                    uploadMonitoringDataToLocal(telemetryStr, "gps")
                
                
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

def obdSerialReader():
    obd_two = serial.Serial(serial_str, baudrate=baudRate)
    
    while True:
        obd_two.flushInput()
        data = obd_two.readline().decode()
        if(len(data.split(",")) == 5):
            uploadMonitoringDataToLocal(data, "obd")
        time.sleep(0.1)

def buzzerForSpeedcheck():
    speedBuzzPin = 5
    beeping = 0
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(speedBuzzPin, GPIO.OUT)
    #GPIO.setwarnings(False)

    timer = time.time_ns()
    while(True):
        gpsReq = requests.get(DB_URL + "getLastGPS")

        if(len(gpsReq.json()) > 0):
            obdReq = requests.get(DB_URL + "getLastOBD")
            if(len(obdReq.json()) > 0):
                carSpeed = obdReq.json()['speed']
                speedLimit = gpsReq.json()['speed']
                if(carSpeed > speedLimit + 10):
                    #GPIO.output(speedBuzzPin, GPIO.HIGH)
                    beeping = 1


        while(time.time_ns() - timer > 1e+9):
            timer = time.time_ns()
        beeping = 0


"""
Prepares a driving session

    1) Prompts user for username and password
    2) Authenticate user
    3) Retrieves session ID for current session from API

Returns session ID
"""
def prepareDrivingSession():
    sessionStart = False
    s_id = -1
    while(sessionStart == False):
        print("Enter a username: ")
        username = "User2"
        print("Enter a password: ")
        password = "9671111"
        payload = {"username": username, "password": password}
        response = requests.get(API_URL+"auth", params=payload)
        uid = response.json()
        if(uid != "Authentication Failed"):
            payload = {"_id": uid}

            response = requests.get(API_URL+"start", params=payload)
            s_id = response.text
            if(s_id != "Error"):
                # print("SESSION ID", s_id)
                sessionStart = True
    
    return s_id


"""
App Initilization Function

    1) Begins driving session
    
    2) Initialize sub systems of application
    2.1) Starts a process for each blindspot sensor
    2.2) Starts a process for the gps sensor
    2.3) Starts a process for listening to serial line
    2.3) Starts a process to await for user commands

"""
def initialization():
    # cameraThread = threading.Thread(target=cameraModule.captureTime)
    # cameraThread.start()
    s_id = prepareDrivingSession()
    for ip in UDP_IPs:
        # mT = threading.Thread(
        #    target=establishUDPConnection, args=(ip, UDP_PORT))
        mT = mp.Process(target=establishUDPConnection, args=(ip, UDP_PORT))
        mT.start()
        monitoring_threads.append(mT)

    gpsT = mp.Process(target=doGPS)
    gpsT.start()

    obdT = mp.Process(target=obdSerialReader)
    obdT.start()

    while(True):
        print("Enter a command: ")
        cmd = input()

        if(cmd == "end"):
            requests.post(DB_URL+"endSession", data=s_id)
            gpsT.kill()
            for th in monitoring_threads:
                th.kill()
            obdT.kill()
            exit(-1)
        


if __name__ == "__main__":
    initialization()
