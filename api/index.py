from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
clients_collection = db["clients"]
reserves_collection = db["reservations"]
orders_collection = db["orders"]

@app.route('/')
def home():
    return 'Api for the restaurant Yonko'

@app.route('/about')
def about():
    return 'About'

@app.route('/api/login', methods=["POST"])  
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    client = clients_collection.find_one({"username": username})
    
    if not client:
        return jsonify({"success": False, "message": "User not exits"}), 401

    # Verificar la contraseña
    if client["password"] == password:
        return jsonify({"success": True, "session": username}), 200
    else:
        return jsonify({"success": False, "message": "Incorrect password"}), 401
    
@app.route('/api/register', methods=["POST"])  
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    
    existUsername = clients_collection.find_one({"username": username})
    
    # Verificar si ya hay un usario con ese nombre de usuario
    if existUsername:
        return jsonify({"success": False, "message": "This username is already in use"}), 401
    else:
        newClient = {
        "email": email,
        "username": username,
        "password": password
        }
        
        addClient = clients_collection.insert_one(newClient)
        
        if addClient:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Failed to create new user"}), 401

@app.route('/api/reservation', methods=["POST"])
def reservation():
    data = request.get_json()

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
        "transact": False, 
        "status": ""
    }
        
    addReserve = reserves_collection.insert_one(newReserve)
        
    if addReserve:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Failed to create the reservation"}), 401

@app.route('/api/reservations', methods=["GET"])
def reservations():
    reservations = list(reserves_collection.find({}))
    for reservation in reservations:
        reservation["_id"] = str(reservation["_id"])
    return jsonify({"success": True, "reservations": reservations}), 200

@app.route('/api/order', methods=["POST"])
def order():
    data = request.get_json()

    username = data.get("username")
    products = data.get("products")
    total = data.get("total")

        
    new_order = {
        "username": username,
        "products": products,
        "total": total,
        "transact": False,  #estado del pedido
        "status": ""
    }
        
    addOrder = orders_collection.insert_one(new_order)
        
    if addOrder:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Failed to create the orders"}), 401

@app.route('/api/orders', methods=["GET"])
def orders():
    orders = list(orders_collection.find({}))
    for order in orders:
        order["_id"] = str(order["_id"])
    return jsonify({"success": True, "orders": orders}), 200


@app.route('/api/order/accept', methods=["POST"])
def accept_order():
    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id or not ObjectId.is_valid(order_id):
        return jsonify({"success": False, "message": "Invalid order id format"}), 400

    try:
        order_objid = ObjectId(order_id)
        update_result = orders_collection.update_one(
            {"_id": order_objid},
            {"$set": {"status": "accept", "transact": True}}
        )
        send_email()  # Llamar a la función para enviar el correo
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating order: {e}"}), 500

    if update_result.modified_count > 0:
        return jsonify({"success": True, "message": "Order accepted and email sent"}), 200
    else:
        return jsonify({"success": False, "message": "Order not found or already updated"}), 404


@app.route('/api/order/decline', methods=["POST"])
def decline_order():
    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id or not ObjectId.is_valid(order_id):
        return jsonify({"success": False, "message": "Invalid order id format"}), 400

    try:
        order_objid = ObjectId(order_id)
        update_result = orders_collection.update_one(
            {"_id": order_objid},
            {"$set": {"status": "decline", "transact": True}}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating order: {e}"}), 500

    if update_result.modified_count > 0:
        return jsonify({"success": True, "message": "Order declined"}), 200
    else:
        return jsonify({"success": False, "message": "Order not found or already updated"}), 404


@app.route('/api/reservation/accept', methods=["POST"])
def accept_reservation():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    if not reservation_id or not ObjectId.is_valid(reservation_id):
        return jsonify({"success": False, "message": "Invalid reservation id format"}), 400

    try:
        reservation_objid = ObjectId(reservation_id)
        update_result = reserves_collection.update_one(
            {"_id": reservation_objid},
            {"$set": {"status": "accept", "transact": True}}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating reservation: {e}"}), 500

    if update_result.modified_count > 0:
        return jsonify({"success": True, "message": "Reservation accepted"}), 200
    else:
        return jsonify({"success": False, "message": "Reservation not found or already updated"}), 404


@app.route('/api/reservation/decline', methods=["POST"])
def decline_reservation():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    if not reservation_id or not ObjectId.is_valid(reservation_id):
        return jsonify({"success": False, "message": "Invalid reservation id format"}), 400

    try:
        reservation_objid = ObjectId(reservation_id)
        update_result = reserves_collection.update_one(
            {"_id": reservation_objid},
            {"$set": {"status": "decline", "transact": True}}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating reservation: {e}"}), 500

    if update_result.modified_count > 0:
        return jsonify({"success": True, "message": "Reservation declined"}), 200
    else:
        return jsonify({"success": False, "message": "Reservation not found or already updated"}), 404

      
handle = app

# def handler(event, context):
#     return app(event, context)
# app.run() # Para ejecutar de manera local el proyecto