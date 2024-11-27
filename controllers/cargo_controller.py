from flask import Blueprint, request, jsonify
import models.cargo_model as cargo_model
from helpers.controler_helpers import json_response_type

cargo_bp = Blueprint("cargo", __name__)

# All cargo routes are unprotected, no need for JWT.
# Route and function to create a cargo entity.
@cargo_bp.route("/cargo", methods=["POST"])
def create_cargo():
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    content = request.get_json()
    weight, item = content.get("weight"), content.get("item")
    if not all([weight, item]): # If attribute missing.
        return jsonify({"Error": "The request object is missing at least one of the required attributes"}), 400
    
    new_cargo = cargo_model.create_cargo(request.base_url, weight, item)
    return jsonify(new_cargo), 201 # If succes.

# Route and function to view a cargo entity.
@cargo_bp.route("/cargo/<cargo_id>", methods=["GET"])
def get_cargo(cargo_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    cargo = cargo_model.get_cargo(request.base_url, cargo_id)
    if not cargo: # If cargo not found.
        return jsonify({"Error": "No cargo with this cargo_id exists"}), 404
    return jsonify(cargo), 200 # If succes.

# Route and function to view all cargo entities.
@cargo_bp.route("/cargo", methods=["GET"])
def get_cargos():
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    q_limit = request.args.get("limit", "5")
    q_offset = request.args.get("offset", "0")
    loads = cargo_model.get_cargos(request.base_url, q_limit, q_offset)
    
    return jsonify(loads), 200 # Success code.

# Route and function to edit subset of cargo attributes.
@cargo_bp.route("/cargo/<cargo_id>", methods=["PATCH"])
def patch_cargo(cargo_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    content = request.get_json()
    weight, item = content.get("weight"), content.get("item")
    cargo, code = cargo_model.update_cargo(request.base_url, "PATCH", cargo_id, {"weight": weight, "item": item})
    
    return jsonify(cargo), code # Code 200 and load if success 404 along with error message if load_id not found.

# Route and function to edit all cargo attributes.
@cargo_bp.route("/cargo/<cargo_id>", methods=["PUT"])
def put_cargo(cargo_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    content = request.get_json()
    if set(content.keys()) != {"weight", "item"}: # Verify correct attributes sent.
        return jsonify({"Error": "Missing attribute/s or too many attributes"}), 400
    
    weight, item = content.get("weight"), content.get("item")
    cargo, code = cargo_model.update_cargo(request.base_url, "PUT", cargo_id, {"weight": weight, "item": item})
    
    return jsonify(cargo), code # Code 303 and load if success 404 along with error message if load_id not found.

# Route and function to delete a cargo entity.
@cargo_bp.route("/cargo/<cargo_id>", methods=["DELETE"])
def delete_cargo(cargo_id):
    success = cargo_model.delete_cargo(cargo_id)
    if not success: # If cargo not found.
        return jsonify({"Error": "No cargo with this cargo_id exists"}), 404
    
    return "", 204 # If success send code 204.

# Route and function to assign cargo to an airplane.
@cargo_bp.route("/airplanes/<airplane_id>/cargo/<cargo_id>", methods={"PUT"})
def assign_cargo(airplane_id, cargo_id):
    found, success, capacity = cargo_model.assign_cargo(airplane_id, cargo_id)
    
    if not found: # If no cargo or no airplane found.
        return jsonify({"Error": "The specified airplane and/or cargo does not exist"}), 404
    if not success: # If cargo already assigned to an airplane.
        return jsonify({"Error": "The cargo is already on an airplane"}), 403
    if not capacity: # If no capacity left on airplane.
        return jsonify({"Error": "The airplane does not have enough capacity left"}), 403
    
    return "", 204 # If success.

# Route and function to remove cargo from an airplane.
@cargo_bp.route("/airplanes/<airplane_id>/cargo/<cargo_id>", methods={"DELETE"})
def remove_cargo(airplane_id, cargo_id):
    found, success = cargo_model.remove_cargo(airplane_id, cargo_id)
    
    if not found: # If no cargo or no airplane found.
        return jsonify({"Error": "The specified airplane and/or cargo does not exist"}), 404
    if not success: # If cargo not assigned to that airplane.
        return jsonify({"Error": "The cargo is not assigned to that airplane"}), 403
    
    return "", 204 # If success.
