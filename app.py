from monitoring_communicator import establishUDPConnection
# import recording
import threading
import gps




# cameraModule = recording.camStuff()

UDP_IPs = ["192.168.0.34"]
UDP_PORT = 2390
monitoring_threads = []

def doGPS():
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    while True:
        try:
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            # To see all report data, uncomment the line below
            # print(report)
            print(report)
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")



def initialization():
    # cameraThread = threading.Thread(target=cameraModule.captureTime)
    # cameraThread.start()

    for ip in UDP_IPs:
        mT = threading.Thread(
            target=establishUDPConnection, args=(ip, UDP_PORT))
        mT.start()
        monitoring_threads.append(mT)

    gpsT = threading.Thread(target=doGPS)
    gpsT.start()
        


if __name__ == "__main__":
    initialization()
