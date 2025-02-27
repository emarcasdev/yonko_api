from flask import jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
reserves_collection = db["reservations"]

def reservation(req):
    data = req.get_json()
    owner = data.get("owner")
    date = data.get("date")
    time = data.get("time")
    name = data.get("name")
    tlfn = data.get("tlfn")
    people = data.get("people")
        
    newReserve = {
        "owner": owner,
        "date": date,
        "time": time,
        "name": name,
        "tlfn": tlfn,
        "people": people,
        "transact": False
    }
        
    addReserve = reserves_collection.insert_one(newReserve)
        
    if addReserve:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Failed to create the reservation"}), 401