from flask import jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
orders_collection = db["orders"]

def order(req):
    data = req.get_json()

    username = data.get("username")
    products = data.get("products")
    total = data.get("total")

        
    new_order = {
        "username": username,
        "products": products,
        "total": total,
        "transact": False  #estado del pedido
    }
        
    addOrder = orders_collection.insert_one(new_order)
        
    if addOrder:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Failed to create the orders"}), 401
    
def get_orders():
    orders = list(orders_collection.find({}, {"_id": 0}))
    return jsonify(orders), 200