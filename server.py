from crypt import methods
from datetime import datetime
from flask import Flask, json, request

api = Flask(__name__)

gpsData = []
blindspotData = []

@api.route("/", methods=["GET"])
def home():
    return "index"

@api.route("/blindspot", methods=['POST'])
def post_blindspot():
    dataObj = {"data": request.data.decode(), "time": datetime.now()}
    blindspotData.append(dataObj)
    return "added"

@api.route("/currentBlindspot", methods=["GET"])
def get_current_blindspot():
    return json.jsonify(blindspotData)

@api.route("/gps", methods=['POST'])
def post_gps():
    decoded = request.data.decode()
    lat,lon = decoded.split(",")
    dataObj = {"lat": lat, "lon": lon, "time": datetime.now()}
    gpsData.append(dataObj)
    return "added"

@api.route("/currentGPS", methods=['GET'])
def get_current_gps():
    return json.jsonify(gpsData)

@api.route("/getLastGPS", methods=['GET'])
def get_last_gps():
    lastGPS = gpsData[len(gpsData) - 1]
    return json.jsonify(lastGPS)



