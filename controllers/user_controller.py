from flask import Blueprint, request, jsonify
import models.user_model as user_model

user_bp = Blueprint("users", __name__)

# Route and function to view all users.
@user_bp.route("/users", methods=["GET"])
def get_users():
    users = user_model.get_users()
    return jsonify(users), 200  # Return all boats in a list with 200 code.

# Methods not supported for /users.
@user_bp.route("/users", methods=["POST","PATCH", "PUT","DELETE"])
def unsuported_routes():
    return jsonify({"Error": "Method not supported"}), 405
