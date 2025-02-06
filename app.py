# app.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  # Import flask-cors
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

API_TOKEN = os.getenv("API_TOKEN")
API_USERNAME = os.getenv("API_USERNAME")
API_URL = "https://api.name.com/v4/domains"
DOMAIN_NAME = os.getenv("DOMAIN_NAME")

def get_auth():
    return (API_USERNAME, API_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/records", methods=["GET"])
def list_records():
    response = requests.get(
        f"{API_URL}/{DOMAIN_NAME}/records",
        auth=get_auth()
    )
    return jsonify(response.json())

@app.route("/api/records", methods=["POST"])
def add_record():
    data = request.json
    response = requests.post(
        f"{API_URL}/{DOMAIN_NAME}/records",
        auth=get_auth(),
        json={
            "host": data["host"],
            "type": data["type"],
            "answer": data["answer"],
            "ttl": 300
        }
    )
    return jsonify(response.json())

@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    data = request.json
    response = requests.put(
        f"{API_URL}/{DOMAIN_NAME}/records/{record_id}",
        auth=get_auth(),
        json={
            "host": data["host"],
            "type": data["type"],
            "answer": data["answer"],
            "ttl": 300
        }
    )
    return jsonify(response.json())

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    response = requests.delete(
        f"{API_URL}/{DOMAIN_NAME}/records/{record_id}",
        auth=get_auth()
    )
    return "", 204

# Proxy endpoint for SSL checker
@app.route("/api/ssl-check/<domain>", methods=["GET"])
def ssl_check(domain):
    try:
        # Make a request to ssl-checker.io
        response = requests.get(f"https://ssl-checker.io/api/v1/check/{domain}")
        response.raise_for_status()  # Raise an error for bad status codes
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)