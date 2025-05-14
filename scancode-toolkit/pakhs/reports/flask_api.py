import os
from flask import Flask, send_file, request, jsonify
from dotenv import load_dotenv
import logging

app = Flask(__name__)
load_dotenv()
AUTHORIZED_KEYS = set(os.getenv("API_KEYS", "").split(","))
JSON_FILE = "depscan-bom.json"

logging.basicConfig(filename="access.log", level=logging.INFO)

@app.route('/vulnerabilities', methods=['GET'])
def get_json_file():
    """Serve JSON file securely with API key authentication"""
    api_key = request.headers.get("X-API-KEY")
    if api_key not in AUTHORIZED_KEYS:
        logging.warning(f"❌ Unauthorized access attempt from {request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 403

    logging.info(f"✅ Valid request from IP: {request.remote_addr}")
    return send_file(JSON_FILE, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=7889)
