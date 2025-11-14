import json
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# --- Configuration ---
app = Flask(__name__)
# Allow CORS for development, though typically not needed when serving frontend from the same host
CORS(app) 
ORDERS_FILE = 'orders.json'

# --- Data Handling Functions ---
def load_orders():
    """Load orders from the JSON file."""
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, 'r') as f:
            # Load with default handling for empty file
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
    except IOError:
        return []

def save_orders(orders):
    """Save orders to the JSON file."""
    # Ensure the list is saved to prevent errors
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

# Initialize the file if it doesn't exist
if not os.path.exists(ORDERS_FILE):
    save_orders([])

# --- API Endpoints ---

@app.route('/')
def serve_frontend():
    """Serves the index.html file on the root URL."""
    try:
        # Assumes index.html is in the same directory as app.py
        return send_file('index.html') 
    except FileNotFoundError:
        return "Error: index.html not found.", 404

@app.route('/orders', methods=['GET'])
def get_orders():
    """Get the full list of orders."""
    orders = load_orders()
    return jsonify(orders)

@app.route('/orders', methods=['POST'])
def add_order():
    """Add a new order."""
    new_order = request.json
    if not new_order or 'udid' not in new_order or 'status' not in new_order or 'date' not in new_order:
        return jsonify({"error": "Missing required order data"}), 400
    
    orders = load_orders()
    # Assign a unique ID (simple implementation)
    new_order['id'] = max([o.get('id', 0) for o in orders] or [0]) + 1
        
    orders.append(new_order)
    save_orders(orders)
    return jsonify(new_order), 201

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order."""
    updated_data = request.json
    if not updated_data:
        return jsonify({"error": "Missing data in request"}), 400

    orders = load_orders()
    
    for i, order in enumerate(orders):
        if order.get('id') == order_id:
            # Update fields while keeping the ID and using defaults if not provided
            order['udid'] = updated_data.get('udid', order['udid'])
            order['status'] = updated_data.get('status', order['status'])
            order['date'] = updated_data.get('date', order['date'])
            
            save_orders(orders)
            return jsonify(order)
            
    return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order by ID."""
    orders = load_orders()
    
    initial_length = len(orders)
    orders = [order for order in orders if order.get('id') != order_id]
    
    if len(orders) < initial_length:
        # Re-save the list
        save_orders(orders)
        return jsonify({"message": f"Order with ID {order_id} deleted"}), 200
        
    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    # Local development server for testing
    app.run(debug=True, port=5000)