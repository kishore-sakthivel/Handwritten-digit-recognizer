import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from flask import Flask, render_template, request, jsonify, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import tensorflow as tf
import sqlite3
import numpy as np
from PIL import Image
import cv2
import os
import io
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =========================
# LOGIN DECORATOR
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# =========================
# LOAD MODEL
# =========================
model = tf.keras.models.load_model("mnist_cnn_model.h5") #Loads trained CNN model.

# =========================
# DATABASE
# =========================
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    image TEXT,
    prediction TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    prediction TEXT,
    confidence REAL
)
""")

conn.commit()

# =========================
# ROOT → LOGIN
# =========================
@app.route("/")
def index():
    return redirect("/login")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            session["role"] = "user"
            return redirect("/home")

        return "Invalid Login"

    return render_template("login.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            return redirect("/login")

        except:
            return "User already exists"

    return render_template("register.html")

# =========================
# GUEST LOGIN
# =========================
@app.route("/guest")
def guest():
    session["user"] = "Guest"
    session["role"] = "guest"
    return redirect("/home")

# =========================
# HOME (DIGIT RECOGNIZER)
# =========================
@app.route("/home")
@login_required
def home():
    return render_template("home.html", user=session["user"])

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# PREDICT
# =========================
@app.route("/predict", methods=["POST"])
def predict():

    data = request.json["image"] #fetch api

    image_data = base64.b64decode(data.split(",")[1])

    image = Image.open(io.BytesIO(image_data)).convert("L") #into grayscale

    img = np.array(image)

    img = 255 - img

    img = cv2.resize(img, (28, 28))

    img = cv2.GaussianBlur(img, (3,3), 0)

    img = img.astype("float32") / 255.0

    img = img.reshape(1, 28, 28, 1)

    prediction = model.predict(img)[0]

    digit = int(np.argmax(prediction))

    confidence = float(np.max(prediction) * 100)

    probabilities = [float(p * 100) for p in prediction] #Used for bar chart

    # SAVE HISTORY
    cursor.execute("""
        INSERT INTO history(username, image, prediction, confidence)
        VALUES (?, ?, ?, ?)
    """, (
        session["user"],
        data,
        str(digit),
        round(confidence, 2)
    ))

    conn.commit()

    return jsonify({
        "digit": digit,
        "confidence": round(confidence, 2),         #sending response to the frontend
        "probabilities": probabilities
    })
# =========================
# SAVE DATASET
# =========================
@app.route("/save_dataset", methods=["POST"])
@login_required
def save_dataset():

    data = request.json
    label = data["label"]

    image_data = data["image"].split(",")[1]

    folder = f"dataset/{label}"
    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/{len(os.listdir(folder))}.png"

    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_data))

    return jsonify({"status": "success"})

# =========================
# HISTORY
# =========================
@app.route("/history")
@login_required
def history():

    cursor.execute("""
        SELECT image, prediction, confidence, created_at
        FROM history
        WHERE username=?
        ORDER BY id DESC
    """, (session["user"],))

    data = cursor.fetchall()

    return render_template("history.html", history=data)

# =========================
# ADMIN (ONLY ADMIN USER)
# =========================
@app.route("/admin")
@login_required
def admin():

    if session["user"] != "admin":
        return "Access Denied ❌"

    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM history")
    total_predictions = cursor.fetchone()[0]

    return render_template("admin.html",
                           users=users,
                           total_predictions=total_predictions)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=False)       