import os
from flask import Flask, request, jsonify, send_file
import pyotp

app = Flask(__name__)

# Load API Key and TOTP Secret from environment variables
VALID_API_KEY = os.getenv("VALID_API_KEY", "default-api-key")  # "default-api-key" as fallback
TOTP_SECRET = os.getenv("TOTP_SECRET", "JBSWY3DPEHPK3PXP")  # Replace with your actual TOTP secret or use the fallback

# Path to the SBOM file
SBOM_FILE_PATH = "sbom_converted.json"

@app.route("/api/v1/sbom", methods=["GET"])
def get_sbom():
    # Check for API key in request headers
    try:
        return send_file(SBOM_FILE_PATH, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "SBOM file not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
