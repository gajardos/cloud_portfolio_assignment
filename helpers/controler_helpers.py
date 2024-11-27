from jose import jwt
from constants import ALGORITHMS, CLIENT_ID, DOMAIN
import json
from urllib.request import urlopen

def json_response_type(request:object) -> bool:
    """Receives a request object and returns True if response type is application/json otherwise returns False."""
    if request.headers.get("Accept") != "application/json": # Verify response type is JSON.
        return False
    return True

# This code is adapted from https://auth0.com/docs/quickstart/backend/python/01-authorization?_ga=2.46956069.349333901.1589042886-466012638.1589042885#create-the-jwt-validation-decorator
# Verify the JWT in the request's Authorization header
def verify_jwt(request):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization'].split()
        token = auth_header[1]
    else:
        return {"Error": "Authorization header is missing"}
    
    jsonurl = urlopen("https://"+ DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        return {"Error": "Invalid header"}
    if unverified_header["alg"] == "HS256":
        return {"Error": "Invalid header"}
    
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=CLIENT_ID,
                issuer="https://"+ DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            return {"Error": "Token expired"}
        
        except jwt.JWTClaimsError:
            return {"Error": "Incorrect claims"}
        
        except Exception:
            return {"Error": "Unable to parse authentication"}

        return payload
    else:
        return {"Error": "No RSA key in JWT"}
