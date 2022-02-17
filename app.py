import json
from monitoring_communicator import establishUDPConnection
# import recording
import threading
import gps
import requests


API_URL = "https://vehicle-tracking-capstone-2021.ue.r.appspot.com/"

# cameraModule = recording.camStuff()

UDP_IPs = ["192.168.0.34"]
UDP_PORT = 2390
monitoring_threads = []

DB_URL = "http://127.0.0.1:5000/"


def uploadMonitoringDataToLocal(data, endpoint):
    requests.post(DB_URL+endpoint, data=data)

def doGPS():
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
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
                uploadMonitoringDataToLocal(dataStr, "gps")
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

def prepareDrivingSession():
    print("Enter a username: ")
    username = input()
    print("Enter a password: ")
    password = input()
    response = requests.get(API_URL+"auth", auth=(username, password))
    responseDat = response.text
    decoded = json.decoder(responseDat)
    userKey = decoded["key"]



def initialization():
    # cameraThread = threading.Thread(target=cameraModule.captureTime)
    # cameraThread.start()
    prepareDrivingSession()
    for ip in UDP_IPs:
        mT = threading.Thread(
            target=establishUDPConnection, args=(ip, UDP_PORT))
        mT.start()
        monitoring_threads.append(mT)

    gpsT = threading.Thread(target=doGPS)
    gpsT.start()
        


if __name__ == "__main__":
    initialization()
