from flask import Flask, jsonify
from octorest import OctoRest

app = Flask(__name__)

# Define OctoPrint connection details
OCTOPRINT_URL = "http://localhost:5000"  # Replace with your OctoPrint URL if different
API_KEY = "5F4B52731CB34B82A7FA33A61B62C267"  # Replace with your actual OctoPrint API key

# Function to create an OctoRest client
def make_client():
    try:
        client = OctoRest(url=OCTOPRINT_URL, apikey=API_KEY)
        print("OctoRest client successfully created")
        return client
    except Exception as e:
        print("Error creating OctoRest client:", e)
        return None

# Initialize a global client
client = make_client()

# Flask route to retrieve terminal logs or printer information
@app.route("/get_terminal_logs", methods=["GET"])
def get_terminal_logs():
    if not client:
        return jsonify({"error": "OctoRest client not initialized"}), 500
    try:
        # Retrieve logs, printer status, or any data you want
        terminal_logs = client.connection_info()  # Adjust method based on desired data
        return jsonify({"logs": terminal_logs})
    except Exception as e:
        print("Error retrieving terminal logs:", e)
        return jsonify({"error": str(e)}), 500

# Add more routes here for different commands, like /start_print, /pause_print, etc.

if __name__ == "__main__":
    # Start the Flask app
    app.run(debug=True, port=5001)  # You can change the port if needed
