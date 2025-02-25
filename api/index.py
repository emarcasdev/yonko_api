from flask import Flask, jsonify, request, session
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Habilitar CORS para tu frontend
CORS(app, supports_credentials=True, origins=["https://restaurante-despliegue.vercel.app"])

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
clients_collection = db["clients"]

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "https://restaurante-despliegue.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, DELETE, PUT"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/login', methods=["POST"])  
def login():
    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"success": False, "message": "Error en el formato JSON"}), 400

    if not data:
        return jsonify({"success": False, "message": "No se enviaron datos"}), 400

    username = data.get("username")
    password = data.get("password")

    client = clients_collection.find_one({"username": username})

    if not client:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

    if client["password"] == password:
        session["client"] = username  
        return jsonify({"success": True, "message": "Login exitoso"}), 200
    else:
        return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

if __name__ == '__main__':
    app.run(debug=True)
