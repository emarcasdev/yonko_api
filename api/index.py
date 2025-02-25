from flask import Flask, jsonify, request, session
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

@app.route('/login', methods=["GET"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")


    client = clients_collection.find_one({"username": username})
    
    if not client:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

    # Verificar la contraseña sin encriptación
    if client["password"] == password:
        session["client"] = username  # Guardar la sesión del usuario
        return jsonify({"success": True, "message": "Login exitoso"}), 200
    else:
        return jsonify({"success": False, "message": "Incorrect passwor"}), 401

# Ruta para cerrar sesión
@app.route('/logout', methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True, "message": "Sesión cerrada"}), 200

@app.route('/register', methods=["POST"])
def register():
    return 'About'

handle = app
# app.run() # Para ejecutar de manera local el proyecto