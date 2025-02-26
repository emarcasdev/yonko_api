from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
clients_collection = db["clients"]

@app.route('/')
def home():
    return 'Api for the restaurant Yonko'

@app.route('/about')
def about():
    return 'About'

@app.route('/api/login', methods=["POST"])  
def login():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"success": False, "message": "Don`t send the data"}), 400
    
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


# Cerrar sesión
@app.route('/logout', methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Sesión cerrada"}), 200

@app.route('/register', methods=["POST"])
def register():
    return 'About'

handle = app

# def handler(event, context):
#     return app(event, context)
# app.run() # Para ejecutar de manera local el proyecto