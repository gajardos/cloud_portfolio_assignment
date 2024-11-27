from google.cloud import datastore
import helpers.model_helpers as model_helpers
import models.cargo_model as cargo_model

# Datastore client to interact with database.
client = datastore.Client()

def create_airplane(base_url: str, tail_number: str, type: str, capacity: str, user: str) -> tuple:
    """Creates new airplane on datastore based on passed attributes."""
    key = client.key("Airplane")
    new_airplane = datastore.Entity(key)
    
    new_airplane.update({"tail_number": tail_number, "type": type, "capacity": capacity, "cargo": [], "pilot": user})
    client.put(new_airplane)
    new_airplane["id"] = new_airplane.key.id # Add Id so it's returned.
    new_airplane["self"] = base_url + "/" + str(new_airplane.key.id) # Build url to self and add to json.
    return new_airplane, 201

def get_airplane(base_url: str, id: str, user: str) -> tuple:
    """Receives the base_url airplane_id and pilot and gets the airplne from datastore. If airplane does not exist or
    user does not have access to it an error is returned."""
    key = client.key("Airplane", int(id))
    airplane = client.get(key)
    
    if not airplane: # Airplane not found.
        return False, {"Error": "Airplane with airplane_id not found."}, 404
    if airplane["pilot"] != user: # User can't access.
        return False, {"Error": "User does not have access to the airplane."}, 401
        
    airplane["id"] = airplane.key.id
    airplane["self"] = base_url
     
    if airplane["cargo"]: # If loaded create self for each cargo.
        for i in range(len(airplane["cargo"])):
            parts = base_url.split("airplanes")
            airplane["cargo"][i]["self"] = parts[0] + "cargo/" + str(airplane["cargo"][i]["id"])
    
    return True, airplane, 200
    
def get_airplanes(base_url: str, q_limit: str, q_offset: str, user: str) -> dict:
    """Function returns all airplanes from google datastore owned by this user, in groups of 5 by using pagination along 
    with the next url."""
    query = client.query(kind="Airplane")
    query.add_filter("pilot", '=', user)
    l_iterator = query.fetch(limit=int(q_limit), offset=int(q_offset))
    pages = l_iterator.pages
    results = list(next(pages)) # Fetch result of query in list form
    
    if l_iterator.next_page_token: # Create the next url using limit and offset.
        next_offset = int(q_offset) + int(q_limit)
        next_url = base_url + "?limit=" + q_limit + "&offset=" + str(next_offset)
    else:
        next_url = None
    
    for airplane in results: # Add id and self to all airplane objects.
        airplane["id"] = airplane.key.id
        airplane["self"] = base_url + "/" +str(airplane.key.id)
        
        if airplane["cargo"]:
            for i in range(len(airplane["cargo"])): # If airplane has cargo construct self for each cargo.
                parts = base_url.split("airplanes")
                airplane["cargo"][i]["self"] = parts[0] + "cargo/" + str(airplane["cargo"][i]["id"])
    
    total = model_helpers.count_items_in_kind("Airplane", user) # Get total number for user.
    airplanes = [dict(airplane) for airplane in results] # List of airplanes.
    response = {"airplanes": airplanes, "total": total, "next": next_url}
    
    return response

def update_airplane(base_url: str, caller: str, id: str, user: str, attributes: dict) -> tuple:
    """Receives the base url, caller, id , user and attributes to update and updates the airplanes attributes. If airplane 
    doesn't exist or invalid user returns an error."""
    key = client.key("Airplane", int(id))
    airplane = client.get(key)
    
    if not airplane: # airplane_id not found.
        return {"Error": "No airplane with this airplane_id exists"}, 404
    if airplane["pilot"] != user: # User can't access airplane.
        return {"Error": "User does not have access to the airplane."}, 401
    
    for attribute in list(attributes.keys()): # If attribute not passed or None passed, delete it prior to update.
        if attributes[attribute] == None:
            del attributes[attribute]
    
    airplane.update(attributes)
    client.put(airplane)
    airplane["id"] = airplane.key.id
    airplane["self"] = base_url
    
    if caller == "PATCH":
        return airplane, 200 # PATCH success.
    else:
        return airplane, 303 # PUT success.

def delete_airplane(id: str, user: str) -> tuple:
    """Receives airplane id and user and deletes the airplane if it's the correct user."""
    key = client.key("Airplane", int(id))
    airplane = client.get(key)
    
    if not airplane: # No airplane found.
        return False, {"Error": "Airplane with airplane_id not found."}, 404
    if airplane["pilot"] != user: # User can't access.
        return False, {"Error": "User does not have access to the airplane."}, 401
    
    if airplane["cargo"]: # Removes airplane as carrier for cargo that was being carried.
        for i in range(len(airplane["cargo"])):
            cargo_model.remove_cargo(id, str(airplane["cargo"][i]["id"]))
    
    client.delete(key)
    return True, "", 204