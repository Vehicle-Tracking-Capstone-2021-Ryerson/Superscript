import socket
import time
from monitoring_communicator import establishUDPConnection
from picamera import PiCamera, PiCameraCircularIO
import multiprocessing as mp
import gps
import requests
import serial
import subprocess

# API_URL = "http://localhost:8080/"
API_URL = "https://vehicle-tracking-capstone-2021.ue.r.appspot.com/"

# cameraModule = recording.camStuff()

# ====================== BLINDSPOT MONITORING VARIABLES ======================
UDP_IPs = ["192.168.30.61", "192.168.30.218", "192.168.30.96", "192.168.30.58"] # UDP IPs for blindspot monitoring sensors
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
                if(time.time() - last_gps_location > 5.0 or last_gps_location == 0):
                    last_gps_location = time.time()
                    payload = {"location_data": dataStr}
                    response = requests.get(API_URL+"speedLimit", params=payload)

                    respData = response.json()[0]
                    street = respData["street"]
                    speedUnit = respData["speedUnit"]
                    speed = respData["speedLimit"]
                    telemetryStr = f"{lat},{lon},{street},{speed},{speedUnit}"
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
    timer = time.time_ns()
    lastBeep = -1
    while(True):
        gpsReq = requests.get(DB_URL + "getLastGPS")

        if(len(gpsReq.json()) > 0):
            obdReq = requests.get(DB_URL + "getLastOBD")
            if(len(obdReq.json()) > 0):
                carSpeed = int(obdReq.json()['speed'])
                speedLimit = int(gpsReq.json()['speed'])

                if(carSpeed > speedLimit + 10 and (time.time_ns() - lastBeep) > 20e+9 and speedLimit != 0):
                    subprocess.Popen(["mpg123","-q","/home/pi/Desktop/Superscript/Sounds/speed_limit_warning.mp3"])
                    lastBeep = time.time_ns()



"""
Prepares a driving session

    1) Prompts user for username and password
    2) Authenticate user
    3) Retrieves session ID for current session from API

Returns session ID
"""
def prepareDrivingSession(username, password):
    sessionStart = False
    s_id = -1
    while(sessionStart == False):
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

def doCamStuff(acc):
    camera = PiCamera(resolution=(1920, 1080))
    stream = PiCameraCircularIO(camera, seconds=60)
    camera.start_recording(stream, format='h264')
    i=1
    try:
        while True:
            camera.wait_recording(60)
            if(acc.value == 1.0):
                stream.copy_to('/home/pi/Desktop/camera/rec_%d.h264' % i)
                i += 1
            elif(acc.value == 2.0):
                raise ValueError
    except ValueError:
        print("Stopping...")
    finally:
        print("IN FINALLY")
        camera.stop_recording()
        stream.close()
        exit(1)

        


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
    # CREATE SOCKET FOR COMMANDS
    s = socket.socket()
    cmdListenerPort = 4000 # PORT FOR 
    host = socket.gethostname()
    s.bind(("127.0.0.1", cmdListenerPort))
    s.listen(5)

    conn, addr  = s.accept()

    username = conn.recv(1024)
    username = username.decode()

    password = conn.recv(1024)
    password = password.decode()

    s_id = prepareDrivingSession(username, password)

    if(s_id != None):
        conn.close()
        exit(1)
    for ip in UDP_IPs:
        mT = mp.Process(target=establishUDPConnection, args=(ip, UDP_PORT))
        mT.start()
        monitoring_threads.append(mT)

    gpsT = mp.Process(target=doGPS)
    gpsT.start()

    obdT = mp.Process(target=obdSerialReader)
    obdT.start()

    speedCheckBuzzer = mp.Process(target=buzzerForSpeedcheck)
    speedCheckBuzzer.start()

    acc = mp.Value('d', 0.0)
    cameraT = mp.Process(target=doCamStuff, args=(acc,))
    cameraT.start()
 

    while(True):
        cmd = conn.recv(1024)
        cmd = cmd.decode()

        if(cmd == "end"):
            requests.get(DB_URL+"end", data=s_id)
            gpsT.kill()
            for th in monitoring_threads:
                th.kill()
            obdT.kill()
            speedCheckBuzzer.kill()
            cameraT.kill()
            conn.close()
            exit(-1)

        elif(cmd == "kbs"):
            speedCheckBuzzer.kill()

        elif(cmd == "acc"):
            acc.value = 1.0

        elif(cmd == "softkill"):
            gpsT.kill()
            for th in monitoring_threads:
                th.kill()
            obdT.kill()
            speedCheckBuzzer.kill()
            acc.value = 2.0
            print("Waiting for camera to die...")
            while(cameraT.is_alive()):
                print()

            exit(1)

        


if __name__ == "__main__":
    initialization()
