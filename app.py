from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from flask_cors import CORS
import os
from dotenv import load_dotenv

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

if __name__ == "__main__":
    app.run(debug=True)
