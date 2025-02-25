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

@app.route('/login', methods=["POST"])  
def login():
    data = request.get_json()  # Nos aseguramos de que obtiene los datos
      # Nos aseguramos de que obtiene los datos
    print(data)
    if not data:
        return jsonify({"success": False, "message": "No se enviaron datos"}), 400
    
    username = data.get("username")
    password = data.get("password")

    client = clients_collection.find_one({"username": username})
    
    if not client:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

    # Verificar la contraseña
    if client["password"] == password:
        session["client"] = username  # Guardamos la sesión del usuario
        return jsonify({"success": True, "message": "Login exitoso"}), 200
    else:
        return jsonify({"success": False, "message": "Incorrect password"}), 401


# Ruta para cerrar sesión
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