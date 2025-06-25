from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os
import math

# Загрузка конфигурации из .env
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["first_name", "last_name", "username", "password"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Не все поля заполнены"}), 400

    # Проверка существующего пользователя
    if mongo.db.users.find_one({"username": data["username"]}):
        return jsonify({"error": "Пользователь уже существует"}), 409

    # Захешировать пароль
    hashed_password = generate_password_hash(data["password"])

    # Сохраняем в БД
    user = {
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "username": data["username"],
        "password": hashed_password
    }
    mongo.db.users.insert_one(user)

    return jsonify({"message": "Пользователь успешно зарегистрирован!"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    user = mongo.db.users.find_one({"username": username})

    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Неверный пароль"}), 401

    return jsonify({
        "message": "Авторизация успешна!",
        "user": {
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    }), 200

from ml_model import check_word

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    word = data.get("word", "")

    if not word:
        return jsonify({"error": "Слово не передано"}), 400

    result = check_word(word)
    return jsonify(result)

# POST /history
@app.route("/history", methods=["POST"])
def post_history():
    data = request.get_json() or {}
    username    = data.get("username")
    input_word  = data.get("input")
    output_word = data.get("output")

    if not username or not input_word or output_word is None:
        return jsonify({"error": "username, input и output обязательны"}), 400

    # Ставим текущее время сервера в UTC
    now = datetime.utcnow()

    mongo.db.history.insert_one({
        "username": username,
        "input":    input_word,
        "output":   output_word,
        "date":     now
    })
    return jsonify({"message": "История сохранена"}), 201


# POST /history
@app.route("/history", methods=["GET"])
def get_history():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username обязателен"}), 400

    records = list(
        mongo.db.history
            .find({"username": username}, {"_id": False})
            .sort("date", -1)
    )

    # Конвертим дату в ISO с Z, чтобы JS правильно воспринимал её как UTC
    for r in records:
        r["date"] = r["date"].isoformat() + "Z"
    return jsonify(records), 200

if __name__ == "__main__":
    app.run(debug=True)
