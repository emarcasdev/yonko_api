from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB usando la URI desde .env
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["yonko_db"]
users_collection = db["clients"]

@app.route('/')
def home():
    return 'Api for the restaurant Yonko'

@app.route('/api/about')
def about():
    return 'About'

handle = app