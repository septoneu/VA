from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import pyotp
import jwt
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration for authentication
VALID_API_KEY = os.getenv("VALID_API_KEY", "Abc123$SecureKey")
TOTP_SECRET = os.getenv("TOTP_SECRET", "KZXW6YTBOIQA32N6")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "A1B2C3D4E5F6G7H8I9J0KLMNOPQRSTUVWXYZ!@#$%^")
CLIENT_ID = os.getenv("CLIENT_ID", "septon_project_client")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "SeptonClientSecret@2024!")
SBOM_FILE_PATH = "sbom_converted.json"
oauth_tokens = {}

# JWT Token creation and verification
def create_jwt():
    expiration = datetime.utcnow() + timedelta(minutes=15)
    token = jwt.encode({"exp": expiration}, JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt(token):
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/terms-of-service")
def terms_of_service():
    return render_template("terms-of-service.html")


@app.route("/submit-credentials", methods=["POST"])
def submit_credentials():
    data = request.json
    step = data.get("step")

    if step == 1:
        api_key = data.get("api_key")
        if api_key != VALID_API_KEY:
            return jsonify({"error": "Invalid API Key"}), 401
        return jsonify({"message": "API Key validated"}), 200

    elif step == 2:
        totp_code = data.get("totp_code")
        totp = pyotp.TOTP(TOTP_SECRET)
        if not totp.verify(totp_code):
            return jsonify({"error": "Invalid TOTP Code"}), 401
        return jsonify({"message": "TOTP validated"}), 200

    elif step == 3:
        jwt_token = create_jwt()
        return jsonify({"token": jwt_token}), 200

    elif step == 4:
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        if client_id == CLIENT_ID and client_secret == CLIENT_SECRET:
            oauth_token = secrets.token_hex(16)
            oauth_tokens[oauth_token] = True  # Store token in memory
            return jsonify({"oauth_token": oauth_token}), 200
        else:
            return jsonify({"error": "Invalid OAuth credentials"}), 401

    return jsonify({"error": "Invalid step"}), 400

@app.route("/retrieve-sbom", methods=["POST"])
def retrieve_sbom():
    # Extract and verify api_key and jwt_token from request
    data = request.json
    api_key = data.get("api_key")
    jwt_token = data.get("jwt_token")

    if api_key != VALID_API_KEY or not verify_jwt(jwt_token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Make a request to the manufacturer server to get the SBOM file without headers
        response = requests.get("http://main.infili.com:5002/api/v1/sbom")

        if response.status_code == 200:
            # Save the downloaded SBOM file
            sbom_file_path = "downloaded_sbom_converted.json"
            with open(sbom_file_path, "wb") as file:
                file.write(response.content)
            return jsonify({"message": "SBOM file retrieved"}), 200
        else:
            return jsonify({"error": "Error retrieving SBOM file"}), response.status_code
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

@app.route("/download", methods=["POST"])
def download():
    # Validate api_key and jwt_token
    data = request.json
    api_key = data.get("api_key")
    jwt_token = data.get("jwt_token")

    if api_key != VALID_API_KEY or not verify_jwt(jwt_token):
        return jsonify({"error": "Unauthorized"}), 401

    sbom_file_path = "downloaded_sbom_converted.json"
    try:
        return send_file(sbom_file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "SBOM file not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
