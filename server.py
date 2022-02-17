from crypt import methods
from datetime import datetime
from flask import Flask, json, request
from google.cloud import storage

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
    print(decoded)
    lat,lon,street,speed = decoded.split(",")
    dataObj = {"lat": lat, "lon": lon, "street": street, "speed": speed, "time": datetime.now()}
    gpsData.append(dataObj)
    return "added"

@api.route("/currentGPS", methods=['GET'])
def get_current_gps():
    return json.jsonify(gpsData)

@api.route("/getLastGPS", methods=['GET'])
def get_last_gps():
    lastGPS = gpsData[len(gpsData) - 1]
    return json.jsonify(lastGPS)

@api.route("/endSession", methods=['POST'])
def post_end_session():
    blob_name = request.data.decode()
    json_object = {}
    json_object["gpsData"] = gpsData
    json_object["blindspotData"] = blindspotData
    json_object_str = json.dumps(json_object)
    storage_client = storage.Client()

    bucket_name = "session-data"
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    blob.upload_from_string(json_object_str, content_type="application/json")
    return "Done"