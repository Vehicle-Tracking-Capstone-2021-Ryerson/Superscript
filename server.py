#!/usr/bin/python3
from datetime import datetime
from flask import Flask, json, request
from markupsafe import escape
from google.cloud import storage

api = Flask(__name__)

gpsData = [{"lat": 31, "lon": 31, "street": "blah", "speed": 50, "time": datetime.now()}]
blindspotData = {"F": [], "B": [], "L": [], "R":[]}
obdData = [{"rpm": 1400, "speed": 48, "throttle": 2400, "airTemp": 0, "fuel": 38.85, "time": datetime.now()}]

@api.route("/", methods=["GET"])
def home():
    return "index"

@api.route("/blindspot", methods=['POST'])
def post_blindspot():
    bSpot = request.data.decode()
    splitBSpot = bSpot.split(",")
    
    dataObj = {"data": splitBSpot[1], "time": datetime.now()}
    blindspotData[splitBSpot[0]].append(dataObj)
    # print(blindspotData)
    return "added"

@api.route("/currentBlindspot", methods=["GET"])
def get_current_blindspot():
    return json.jsonify(blindspotData)

@api.route("/gps", methods=['POST'])
def post_gps():
    decoded = request.data.decode()
    # print(decoded)
    lat,lon,street,speed = decoded.split(",")
    dataObj = {"lat": lat, "lon": lon, "street": street, "speed": speed, "time": datetime.now()}
    gpsData.append(dataObj)
    return "added"

@api.route("/obd", methods=['POST'])
def post_obd():
    decoded = request.data.decode()
    rpm, speed, throttle, airTemp, fuelLevel = decoded.split(",")
    dataObj = {"rpm": rpm, "speed": speed, "throttle": throttle, "airTemp": airTemp, "fuel": fuelLevel, "time": datetime.now()}
    # print(dataObj)
    obdData.append(dataObj)
    return "added"

@api.route("/currentGPS", methods=['GET'])
def get_current_gps():
    return json.jsonify(gpsData)

@api.route("/getLastGPS", methods=['GET'])
def get_last_gps():
    if(len(gpsData) > 0):
        lastGPS = gpsData[len(gpsData) - 1]
        return json.jsonify(lastGPS)
    return json.jsonify([])

@api.route("/getLastBlindspot/<pos>", methods=['GET'])
def get_last_blindspot(pos):
    pos = escape(pos)
    BSMLen = len(blindspotData[pos])
    if(BSMLen > 0):
        lastBSM = blindspotData[pos][len(blindspotData[pos]) - 1]
        return json.jsonify(lastBSM)
    else:
        return json.jsonify([])

@api.route("/getLastOBD", methods=['GET'])
def get_last_OBD():
    if(len(obdData) > 0):
        lastOBD = obdData[len(obdData) - 1]
        return json.jsonify(lastOBD)
    return json.jsonify([])
    

@api.route("/endSession", methods=['POST'])
def post_end_session():
    blob_name = request.data.decode()
    json_object = {}
    json_object["gpsData"] = gpsData
    json_object["blindspotData"] = blindspotData
    json_object["OBD_data"] = obdData
    json_object_str = json.dumps(json_object)
    print(json_object_str)
    storage_client = storage.Client()

    bucket_name = "session-data"
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    blob.upload_from_string(json_object_str, content_type="application/json")
    return "Done"