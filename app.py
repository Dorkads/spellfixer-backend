from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_cors import CORS
import os
from dotenv import load_dotenv
import jwt
import datetime

from functools import wraps
from flask import request

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

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
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Неверный логин или пароль"}), 401

    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "message": "Авторизация успешна!",
        "token": token,
        "user": {
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    }), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Токен не предоставлен'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"_id": ObjectId(data["user_id"])})
        except Exception as e:
            return jsonify({'error': 'Недействительный токен'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


if __name__ == "__main__":
    app.run(debug=True)
