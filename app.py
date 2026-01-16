from flask import Flask, render_template, jsonify, request
import os
import requests
from dotenv import load_dotenv
from ssl_checker import check_multiple_domains

load_dotenv()

app = Flask(__name__)
app.debug = True

# Configuration
API_TOKEN = os.getenv("API_TOKEN")
API_USERNAME = os.getenv("API_USERNAME")
API_URL = "https://api.name.com/v4/domains"
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "srx.im")

def get_auth():
    return (API_USERNAME, API_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ssl")
def ssl_page():
    return render_template("ssl.html")

@app.route("/api/records", methods=["GET"])
def list_records():
    response = requests.get(f"{API_URL}/{DOMAIN_NAME}/records", auth=get_auth())
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

@app.route("/api/records/bulk", methods=["POST"])
def add_bulk_records():
    data = request.json
    domains = data.get("domains", [])
    ip_address = data.get("ip_address", "")
    record_type = data.get("type", "A")
    results = {"success": [], "failed": []}
    
    for domain in domains:
        domain = domain.strip()
        if not domain: continue
        try:
            response = requests.post(
                f"{API_URL}/{DOMAIN_NAME}/records",
                auth=get_auth(),
                json={"host": domain, "type": record_type, "answer": ip_address, "ttl": 300}
            )
            if response.status_code in [200, 201]:
                results["success"].append({"domain": domain, "ip": ip_address})
            else:
                results["failed"].append({"domain": domain, "error": response.text})
        except Exception as e:
            results["failed"].append({"domain": domain, "error": str(e)})
    return jsonify(results)

@app.route("/api/records/bulk-delete-by-hostname", methods=["POST"])
def bulk_delete_by_hostname():
    data = request.json
    # Clean input: get list of subdomains and ignore empty lines
    hosts_to_delete = [d.strip() for d in data.get("domains", []) if d.strip()]
    
    # 1. Fetch all current records from Name.com
    all_res = requests.get(f"{API_URL}/{DOMAIN_NAME}/records", auth=get_auth())
    
    if all_res.status_code != 200:
        return jsonify({"error": "Failed to fetch records from Name.com"}), 500
    
    # The API returns an object where "records" is the list
    all_records = all_res.json().get("records", [])
    
    results = {"success": [], "failed": []}
    
    # 2. Match and Delete
    for host in hosts_to_delete:
        # Use .get("host") to avoid KeyError. 
        # Note: Name.com uses empty string "" or omits "host" for the root domain.
        matches = [r for r in all_records if r.get("host") == host]
        
        if not matches:
            results["failed"].append({"domain": host, "error": "No matching record found in Name.com"})
            continue
            
        for match in matches:
            record_id = match.get("id")
            try:
                del_res = requests.delete(
                    f"{API_URL}/{DOMAIN_NAME}/records/{record_id}", 
                    auth=get_auth()
                )
                if del_res.status_code in [200, 204]:
                    results["success"].append(host)
                else:
                    results["failed"].append({"domain": host, "error": del_res.text})
            except Exception as e:
                results["failed"].append({"domain": host, "error": str(e)})
                
    return jsonify(results)

@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    data = request.json
    response = requests.put(
        f"{API_URL}/{DOMAIN_NAME}/records/{record_id}",
        auth=get_auth(),
        json={"host": data["host"], "type": data["type"], "answer": data["answer"], "ttl": 300}
    )
    return jsonify(response.json())

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    requests.delete(f"{API_URL}/{DOMAIN_NAME}/records/{record_id}", auth=get_auth())
    return "", 204

@app.route("/api/ssl-check", methods=["POST"])
def check_ssl():
    domains = request.json.get('domains', [])
    return jsonify(check_multiple_domains(domains))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
