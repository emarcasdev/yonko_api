from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import ObjectId



import smtplib



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






# Función para enviar correo
def send_email():
    sender_email = "yonkorestaurante@gmail.com"
    sender_password = "jgvm mtwl frsw cjmr"  # Usar una Contraseña de Aplicación en vez de la contraseña normal

    receiver_email = "agusskate34@gmail.com"
    subject = "Pedido Aceptado - Yonko Restaurant"
    message = "Tu pedido ha sido aceptado. ¡Gracias por confiar en nosotros! 🍽️"

    email_text = f"Subject: {subject}\n\n{message}"

    try:
        # Conexión con el servidor SMTP de Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()
        print("📧 Correo enviado correctamente")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)


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
        "transact": False
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
        "transact": False  #estado del pedido
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


# Ruta para enviar el correo
@app.route('/api/order/accept', methods=["POST"])
def accept_order():
    # Llamar a la función para enviar el correo
    send_email()
    
    return jsonify({"success": True, "message": "Order accepted and email sent"}), 200

# ❌ Rechazar pedido y eliminarlo
@app.route('/api/order/decline', methods=["POST"])
def decline_order():
    data = request.get_json()
    order_id = data.get("order_id")

    delete_result = orders_collection.delete_one({"_id": ObjectId(order_id)})

    if delete_result.deleted_count > 0:
        return jsonify({"success": True, "message": "Order declined and removed"}), 200
    else:
        return jsonify({"success": False, "message": "Order not found","id":order_id}), 404


#Reservas
@app.route('/api/reservation/accept', methods=["POST"])
def accept_reservation():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    # Validar que el reservation_id exista y tenga formato válido
    if not reservation_id or not ObjectId.is_valid(reservation_id):
        return jsonify({"success": False, "message": "Invalid reservation id format"}), 400

    try:
        reservation_objid = ObjectId(reservation_id)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error converting reservation id: {e}"}), 500

    # Actualizar la reserva para marcarla como aceptada (transact: True)
    update_result = reserves_collection.update_one(
        {"_id": reservation_objid},
        {"$set": {"transact": True}}
    )

    if update_result.modified_count > 0:
        return jsonify({"success": True, "message": "Reservation accepted"}), 200
    else:
        return jsonify({"success": False, "message": "Reservation not found"}), 404


@app.route('/api/reservation/decline', methods=["POST"])
def decline_reservation():
    # data = request.get_json()
    # reservation_id = data.get("reservation_id")

    # # Validar que el reservation_id exista y tenga formato válido
    # if not reservation_id or not ObjectId.is_valid(reservation_id):
    #     return jsonify({"success": False, "message": "Invalid reservation id format"}), 400

    # try:
    #     reservation_objid = ObjectId(reservation_id)
    # except Exception as e:
    #     return jsonify({"success": False, "message": f"Error converting reservation id: {e}"}), 500

    delete_result = reserves_collection.delete_one({"id": "1"})

    if delete_result.deleted_count > 0:
        return jsonify({"success": True, "message": "Reservation declined and removed"}), 200
    else:
        return jsonify({"success": False, "message": "Reservation not found", "id": reservation_id}), 404

      
handle = app

# def handler(event, context):
#     return app(event, context)
# app.run() # Para ejecutar de manera local el proyecto