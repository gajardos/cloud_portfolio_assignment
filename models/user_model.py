from google.cloud import datastore

# Datastore client to interact with database.
client = datastore.Client()

def create_user(sub: str)-> object:
    """Receives user jwt and creates it on google datastore."""
    key = client.key("User")
    new_user = datastore.Entity(key)
    
    new_user.update({"ID": sub})
    client.put(new_user)

def get_users()-> list:
    """Function returns all users that have been created from the google datastore."""
    query = client.query(kind="User")
    results = list(query.fetch()) # Fetch result of query in list form
    users = [dict(user) for user in results]
    return users

def user_exists(sub: str) -> bool:
    """Checks if passed sub matches a created user."""
    query = client.query(kind="User")
    query.add_filter('ID', '=', sub)
    results = list(query.fetch()) # Fetch result of query in list form.
    
    if results: # If user exists.
        return True
    return False # If user does not exist.