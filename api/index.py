from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
# Importamos las funciones de reservas y pedidos
from reservations import reservation, get_reservations
from orders import order, get_orders

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
def create_reservation():
    return reservation(request)

@app.route('/api/reservations', methods=["GET"])
def get_all_reservations():
    return get_reservations()

@app.route('/api/order', methods=["POST"])
def create_order():
    return order(request)

@app.route('/api/orders', methods=["GET"])
def get_all_orders():
    return get_orders()
      
handle = app

# def handler(event, context):
#     return app(event, context)
# app.run() # Para ejecutar de manera local el proyecto