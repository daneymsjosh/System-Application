from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import join_room, leave_room, send, SocketIO
import firebase_admin
from firebase_admin import credentials, auth, firestore
import random
from string import ascii_uppercase
from ciphers import enhanced_rail_fence_encrypt, enhanced_rail_fence_decrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "railfence"
socketio = SocketIO(app)

cred = credentials.Certificate("sdk_key/thesis-system-key.json")
# cred = credentials.Certificate("/home/thesisvibe/mysite/sdk_key/thesis-system-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/", methods=["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    return render_template("signup.html")

@app.route("/home", methods=["POST", "GET"])
def home():    
    return render_template("home.html")

@app.route("/room")
def room():
    return render_template("room.html")

@app.route("/encrypt", methods=["POST"])
def encrypt_message():
    data = request.json
    message = data["message"]
    encrypted_message, key = enhanced_rail_fence_encrypt(message)
    return jsonify({"encrypted_message": encrypted_message, "key": key})

@app.route("/decrypt", methods=["POST"])
def decrypt_message():
    data = request.json
    encrypted_message = data["encrypted_message"]
    key = data["key"]
    decrypted_message = enhanced_rail_fence_decrypt(encrypted_message, key)
    return jsonify({"decrypted_message": decrypted_message})

if __name__ == "__main__":
    socketio.run(app, debug=True)