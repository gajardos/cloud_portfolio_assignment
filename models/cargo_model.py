from google.cloud import datastore
import helpers.model_helpers as model_helpers
from datetime import datetime

# Datastore client to interact with database.
client = datastore.Client()

def create_cargo(base_url: str, weight: str, item: str)-> object:
    """Receives load info and creates it on google datastore."""
    key = client.key("Cargo")
    new_cargo = datastore.Entity(key)
    
    new_cargo.update({"weight": weight, "carrier": None, "item": item, "last_update": datetime.now()})
    client.put(new_cargo)
    new_cargo["id"] = new_cargo.key.id # Add Id so it's returned.
    new_cargo["self"] = base_url + "/" +str(new_cargo.key.id) # Build url to self and add to json.
    return new_cargo

def get_cargo(base_url: str, id: str)-> object:
    """Receives the base_url and id and returns the cargo information from google datastore."""
    key = client.key("Cargo", int(id))
    cargo = client.get(key)
    
    if not cargo: # If load not found.
        return None
    
    cargo["id"] = cargo.key.id
    cargo["self"] = base_url
     
    if cargo["carrier"] is not None: # If cargo has a carrier construct self url to carrier.
        parts = base_url.split("cargo")
        cargo["carrier"]["self"] = parts[0] + "airplanes/" + str(cargo["carrier"]["id"])
    
    return cargo

def get_cargos(base_url: str, q_limit: str, q_offset: str)-> dict:
    """Function returns all loads from google datastore, in groups of 5 by using pagination along with the next url."""
    query = client.query(kind="Cargo")
    l_iterator = query.fetch(limit=int(q_limit), offset=int(q_offset))
    pages = l_iterator.pages
    results = list(next(pages)) # Fetch result of query in list form
    
    if l_iterator.next_page_token: # Create the next url using limit and offset.
        next_offset = int(q_offset) + int(q_limit)
        next_url = base_url + "?limit=" + q_limit + "&offset=" + str(next_offset)
    else:
        next_url = None
    
    for cargo in results: # Add id and self to all cargo objects.
        cargo["id"] = cargo.key.id
        cargo["self"] = base_url + "/" +str(cargo.key.id)
        
        if cargo["carrier"] is not None: # If cargo has a carrier construct self url for carrier.
            parts = base_url.split("loads")
            cargo["carrier"]["self"] = parts[0] + "airplanes/" + str(cargo["carrier"]["id"])
    
    total = model_helpers.count_items_in_kind("Cargo", None) # Get total number, None for no user.
    loads = [dict(load) for load in results] # List of loads.
    response = {"Cargos": loads, "total": total, "next": next_url}
    
    return response

def update_cargo(base_url: str, caller: str, id: str, attributes: dict) -> tuple:
    """Receives the base url, caller, id and attributes to update and updates the cargo attributes. If cargo doesn't exist
    returns an error."""
    key = client.key("Cargo", int(id))
    cargo = client.get(key)
    if not cargo: # cargo_id not found.
        return {"Error": "No cargo with this cargo_id exists"}, 404
    
    for attribute in list(attributes.keys()): # If attribute not passed or None passed, delete it prior to update.
        if attributes[attribute] == None:
            del attributes[attribute]
    
    attributes.update({"last_update": datetime.now()})
    cargo.update(attributes)
    client.put(cargo)
    cargo["id"] = cargo.key.id
    cargo["self"] = base_url
    
    if caller == "PATCH":
        return cargo, 200 # PATCH success
    else:
        return cargo, 303 # PUT success.
    
def delete_cargo(id: str)-> bool:
    """Deletes the cargo from datastore if it exists."""
    key = client.key("Cargo", int(id))
    cargo = client.get(key)
    
    if not cargo: # No cargo found.
        return False
    
    if cargo["carrier"]: # Remove cargo from airplane if being carried.
        remove_cargo(str(cargo["carrier"]["id"]), id)
    
    client.delete(key)
    return True

def assign_cargo(airplane_id: str, cargo_id: str)-> tuple:
    """Receives the airplane_id and cargo_id and assigns the cargo to that airplane."""
    cargo_key = client.key("Cargo", int(cargo_id))
    cargo = client.get(cargo_key)
    airplane_key = client.key("Airplane", int(airplane_id))
    airplane = client.get(airplane_key)
    found, success, capacity = True, True, True
    
    if not cargo or not airplane: # If cargo or airplane not found.
        found = False
        return found, success, capacity

    if cargo["carrier"] is not None: # If cargo already on an airplane.
        success = False
        return found, success, capacity
    
    if not model_helpers.enough_capacity_left(airplane, cargo): # If not enough capacity left on airplane.
        capacity = False
        return found, success, capacity
    
    cargos = airplane["cargo"]
    cargos.append({"id": cargo.key.id, "weight": cargo["weight"]})
    cargo.update({"carrier": {"id": airplane.key.id, "tail_number": airplane["tail_number"]}}) # Add carrier to cargo.
    airplane.update({"cargo": cargos}) # Add cargos to cargo of airplane.
    client.put(cargo)
    client.put(airplane)
    
    return found, success, capacity

def remove_cargo(airplane_id: str, cargo_id: str)-> tuple:
    """Receives airplane_id and cargo_id and removes the cargo from the airplane."""
    cargo_key = client.key("Cargo", int(cargo_id))
    cargo = client.get(cargo_key)
    airplane_key = client.key("Airplane", int(airplane_id))
    airplane = client.get(airplane_key)
    found, success = True, True
    
    if not cargo or not airplane: # If cargo or airplane not found.
        found = False
        return found, success
    
    if not cargo["carrier"] or cargo["carrier"]["id"] != int(airplane_id): # If cargo not on airplane.
        success = False
        return found, success
    
    cargos = airplane["cargo"]
    cargos = [cargo for cargo in cargos if cargo["id"] != int(cargo_id)]
    cargo.update({"carrier": None}) # Remove carrier from cargo.
    airplane.update({"cargo": cargos}) # Remove cargo from airplane.
    client.put(cargo)
    client.put(airplane)
    
    return found, success
