from flask import Flask
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from controllers.airplane_controller import airplane_bp
from controllers.cargo_controller import cargo_bp
from controllers.user_controller import user_bp
import models.user_model as user_model
from constants import CLIENT_ID, CLIENT_SECRET, DOMAIN

app = Flask(__name__)

app.register_blueprint(airplane_bp)
app.register_blueprint(cargo_bp)
app.register_blueprint(user_bp)
app.secret_key = 'SECRET_KEY'

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_base_url="https://" + DOMAIN,
    access_token_url="https://" + DOMAIN + "/oauth/token",
    authorize_url="https://" + DOMAIN + "/authorize",
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{DOMAIN}/.well-known/openid-configuration'
)

# Basic route for whole app.
@app.route('/')
def index():
    
    return render_template("welcome.html")

# Login to Auth0 route.
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

# Callback route.
@app.route("/callback")
def callback():
    try:
        # Process Auth0 callback as usual.
        token = oauth.auth0.authorize_access_token()
        session["jwt"] = token["id_token"]
        session["sub"] = token["userinfo"]["sub"]
        
        return redirect(url_for("user_info"))
    except Exception as e: # Exception if failure.
        print(f"Callback error: {e}")
        return f"An error occurred: {e}", 500

# User info route, displays user ID and JWT to user.
@app.route("/user-info")
def user_info():
    jwt = session.get("jwt")
    sub = session.get("sub")
    
    if not jwt or not sub: # If error.
        return "JWT or sub not found please login first", 401
    
    if not user_model.user_exists(sub): # Create new user if user matching sub doesn't exist.
        user_model.create_user(sub)
        
    return f"ID: {sub}<br>JWT: {jwt}"

# Logout route.
@app.route("/logout")
def logout():
    session.clear()
    params = {"returnTo": url_for("index", _extrenal=True), "client_id": CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
