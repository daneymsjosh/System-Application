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
firebase_admin.initialize_app(cred)

db = firestore.client()

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.get_user_by_email(email)
            # Handle login and session management here
            # You can redirect the user to another page after successful login
            session["user"] = user.uid
            return redirect(url_for("home"))
        except Exception as e:
            error = str(e)
            return render_template("login.html", error=error)
    return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            user = auth.create_user(email=email, password=password)
            # Save user to Firestore Users collection
            db.collection('Users').document(user.uid).set({'email': email, 'username': username})
            # You can redirect the user to another page after successful signup
            return redirect(url_for("login"))
        except Exception as e:
            error = str(e)
            return render_template("signup.html", error=error)
    return render_template("signup.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route("/encrypt", methods=["POST"])
def encrypt_message():
    data = request.get_json()
    plaintext = data['plaintext']
    ciphertext, key = enhanced_rail_fence_encrypt(plaintext)
    return jsonify({'ciphertext': ciphertext, 'key': key})

@app.route("/decrypt", methods=["POST"])
def decrypt_message():
    data = request.get_json()
    ciphertext = data['ciphertext']
    key = data['key']
    plaintext = enhanced_rail_fence_decrypt(ciphertext, key)
    return jsonify({'plaintext': plaintext})

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }

    # Encrypt outgoing message
    encrypted_message, key = enhanced_rail_fence_encrypt(data["data"])
    content["message"] = encrypted_message

    decrypted_message = enhanced_rail_fence_decrypt(encrypted_message, key)
    content["decrypted_message"] = decrypted_message

    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")
    print(f"{session.get('name')} encrypted: {content['message']}")
    print(f"{session.get('name')} decrypted: {content['decrypted_message']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)