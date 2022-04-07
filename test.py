import requests
import socket


API_URL = "https://vehicle-tracking-capstone-2021.ue.r.appspot.com/"
DB_URL = "http://127.0.0.1:5000/" # Local Database URL

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

    print("awaiting connection...")
    conn, addr  = s.accept()

    username = conn.recv(1024)
    username = username.decode()
    print("GOT USER "+username)
    password = conn.recv(1024)
    password = password.decode()
    print("GOT PASSWORD "+ password)
    s_id = prepareDrivingSession(username, password)

    if(s_id != None):
        print("Invalid username and password!")
        conn.close()
        exit(1)


    """
    gpsT = mp.Process(target=doGPS)
    gpsT.start()

    obdT = mp.Process(target=obdSerialReader)
    obdT.start()

    speedCheckBuzzer = mp.Process(target=buzzerForSpeedcheck)
    speedCheckBuzzer.start()

    acc = mp.Value('d', 0.0)
    cameraT = mp.Process(target=doCamStuff, args=(acc,))
    cameraT.start()
 
    """
    while(True):
        cmd = conn.recv(1024)
        cmd = cmd.decode()

        if(cmd == "end"):
            requests.get(DB_URL+"end", data=s_id)
            print("END")

            conn.close()
            exit(-1)

        elif(cmd == "acc"):
            print("ACC CHANGE")
