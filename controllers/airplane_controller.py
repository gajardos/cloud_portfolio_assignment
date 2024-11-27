from flask import Blueprint, request, jsonify
import models.airplane_model as airplane_model
from helpers.controler_helpers import verify_jwt, json_response_type

airplane_bp = Blueprint("airplanes", __name__)

# All airplane routes are protected, valid jwt matching the user required.
# Create an airplane.
@airplane_bp.route("/airplanes", methods=["POST"])
def create_airplane():
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    payload = verify_jwt(request)
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    content = request.get_json()
    if set(content.keys()) != {"tail_number", "type", "capacity"}: # Verify correct attributes sent, if not send error message and code 400.
        return jsonify({"Error": "Missing attribute/s or too many attributes"}), 400
    
    tail_number, type, capacity = content.get("tail_number"), content.get("type"), content.get("capacity")
    new_airplane, code = airplane_model.create_airplane(request.base_url, tail_number, type, capacity, payload["sub"])
    
    return jsonify(new_airplane), code # new_airplane and code 201 if successful.

# Get an airplane.
@airplane_bp.route("/airplanes/<airplane_id>", methods=["GET"])
def get_airplane(airplane_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    payload = verify_jwt(request)
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    success, airplane, code = airplane_model.get_airplane(request.base_url, airplane_id, payload["sub"])
    if not success: # If airplane not found code 404 or wrong pilot/user trying to access code 401.
        return jsonify(airplane), code
    
    return jsonify(airplane), code # If airplane found send airplane and code 200.

# Get all user airplanes.
@airplane_bp.route("/airplanes", methods=["GET"])
def get_airplanes():
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    payload = verify_jwt(request)
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    q_limit = request.args.get("limit", "5")
    q_offset = request.args.get("offset", "0")
    airplanes = airplane_model.get_airplanes(request.base_url, q_limit, q_offset, payload["sub"])
    
    return jsonify(airplanes), 200

# Route and function to edit subset of airplane attributes.
@airplane_bp.route("/airplanes/<airplane_id>", methods=["PATCH"])
def patch_airplane(airplane_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    payload = verify_jwt(request)
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    content = request.get_json()
    tail_number, type, capacity = content.get("tail_number"), content.get("type"), content.get("capacity")
    cargo, code = airplane_model.update_airplane(request.base_url, "PATCH", airplane_id, payload["sub"],
                                                 {"tail_number": tail_number, "type": type, "capacity": capacity})
    return jsonify(cargo), code # Code 200 and airplane if success 404 or 401 along with error message if error.

# Route and function to edit all airplane attributes.
@airplane_bp.route("/airplanes/<airplane_id>", methods=["PUT"])
def put_airplane(airplane_id):
    if not json_response_type(request): # If response type not json.
        return jsonify({"Error": "Unsupported response type"}), 406
    
    payload = verify_jwt(request)
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    content = request.get_json()
    if set(content.keys()) != {"tail_number", "type", "capacity"}: # Verify correct attributes sent.
        return jsonify({"Error": "Missing attribute/s or too many attributes"}), 400
    
    tail_number, type, capacity = content.get("tail_number"), content.get("type"), content.get("capacity")
    cargo, code = airplane_model.update_airplane(request.base_url, "PUT", airplane_id, payload["sub"],
                                                 {"tail_number": tail_number, "type": type, "capacity": capacity})
    return jsonify(cargo), code # Code 303 and airplane if success 404 or 401 along with error message if error.

# Delete airplane of passed user.
@airplane_bp.route("/airplanes/<airplane_id>", methods=["DELETE"])
def delete_airplane(airplane_id):
    payload = verify_jwt(request)
    
    if "Error" in payload: # If invalid JWT or JWT missing, return error and code 401.
        return jsonify(payload), 401
    
    success, message, code = airplane_model.delete_airplane(airplane_id, payload["sub"])
    if not success: # If airplane not found.
        return jsonify(message), code
    
    return message, code # If success send code 204.
