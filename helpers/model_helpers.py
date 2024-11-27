from google.cloud import datastore

# Datastore client to interact with database.
client = datastore.Client()

def count_items_in_kind(name: str, user: str) -> int:
    """Returns the total numbers of items in datastore collection based on name. Also filters by user if airplane type."""
    query = client.query(kind=name)
    results = list(query.fetch())
    
    # If user passed filter airplanes to only include those of passed user.
    if user: results = [airplane for airplane in results if airplane["pilot"] == user]
    return len(results)

def enough_capacity_left(airplane: object, cargo: object) -> bool:
    """Receives the the airplane and cargo that wants to be added and checks if there's enough capacity to add the cargo.
    Returns True if there is and False if not."""
    cargos = airplane["cargo"]
    total = 0
    for cargo in cargos:
        total += cargo["weight"]
    
    if total + cargo["weight"] > airplane["capacity"]: return False
    else: return True
