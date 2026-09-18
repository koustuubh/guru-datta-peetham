import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import db
import youtube_service

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "divine-blessings-secret-key-2026")

@app.route("/")
def index():
    """Serves the Divine Store frontend."""
    return render_template("index.html")

# --- REST API Endpoints ---

@app.route("/api/health", methods=["GET"])
def health():
    """Returns database connection status and server info."""
    try:
        status_info = db.get_health_status()
        return jsonify(status_info)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/retry-oracle", methods=["POST"])
def retry_oracle():
    """Attempts to reconnect to Oracle DBMS."""
    success = db.init_oracle_connection()
    status_info = db.get_health_status()
    return jsonify({
        "success": success,
        "health": status_info
    })

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns all product categories."""
    try:
        categories = db.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products", methods=["GET"])
def get_products():
    """Returns products filtered by category, search term, or featured status."""
    category_id = request.args.get("category_id")
    search = request.args.get("search")
    featured_only = request.args.get("featured", "").lower() in ("true", "1")

    try:
        products = db.get_products(
            category_id=category_id,
            search=search,
            featured_only=featured_only
        )
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Returns a single product by ID."""
    try:
        product = db.get_product(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products", methods=["POST"])
def create_product():
    """Creates a new product in the store (Admin)."""
    data = request.get_json()
    if not data or not data.get("name") or not data.get("price") or not data.get("category_id"):
        return jsonify({"error": "Name, price, and category_id are required fields"}), 400

    try:
        new_prod = db.create_product(data)
        return jsonify(new_prod), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates an existing product (Admin)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    try:
        updated = db.update_product(product_id, data)
        if not updated:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(updated)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Deletes a product by ID (Admin)."""
    try:
        db.delete_product(product_id)
        return jsonify({"success": True, "message": f"Product {product_id} deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders", methods=["POST"])
def place_order():
    """Places a new customer order."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Order payload required"}), 400

    order_info = data.get("customer")
    items = data.get("items")

    if not order_info or not items:
        return jsonify({"error": "Customer information and cart items are required"}), 400

    required_fields = ["customer_name", "customer_email", "customer_phone", "shipping_address"]
    for field in required_fields:
        if not order_info.get(field):
            return jsonify({"error": f"Missing required customer field: {field}"}), 400

    if len(items) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    try:
        order_result = db.create_order(order_info, items)
        return jsonify(order_result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Returns all placed orders."""
    try:
        orders = db.get_orders()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticates admin or devotee."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = db.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({
        "success": True,
        "user": {
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    })

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Registers a new devotee account."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone", "")
    email = data.get("email", "")

    if not username or not password or not full_name:
        return jsonify({"error": "Username, password and Full Name required"}), 400

    try:
        new_user = db.register_user(username, password, full_name, phone, email)
        return jsonify({"success": True, "user": new_user}), 201
    except Exception as e:
        return jsonify({"error": "Username already exists or invalid data"}), 400

@app.route("/api/admin/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    """Admin endpoint to update order status."""
    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    try:
        db.update_order_status(order_id, new_status)
        return jsonify({"success": True, "order_id": order_id, "status": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/orders/<int:order_id>/payment", methods=["PUT"])
def update_order_payment(order_id):
    """Admin endpoint to verify or update transaction payment status and UTR."""
    data = request.get_json() or {}
    payment_status = data.get("payment_status")
    utr_number = data.get("utr_number")
    if not payment_status:
        return jsonify({"error": "Payment status is required"}), 400
    try:
        db.update_order_payment(order_id, payment_status, utr_number)
        return jsonify({"success": True, "order_id": order_id, "payment_status": payment_status, "utr_number": utr_number})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>/price", methods=["PUT"])
def update_product_price(product_id):
    """Admin endpoint to update product price (rate) and optional stock."""
    data = request.get_json() or {}
    price = data.get("price")
    stock = data.get("stock_quantity")
    if price is None:
        return jsonify({"error": "Price is required"}), 400
    try:
        updated = db.update_product_price(product_id, price, stock)
        if not updated:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(updated)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/issues", methods=["POST"])
def submit_issue():
    """Devotee endpoint to submit an issue or query."""
    data = request.get_json() or {}
    devotee_name = data.get("devotee_name")
    phone = data.get("phone")
    description = data.get("description")
    if not devotee_name or not phone or not description:
        return jsonify({"error": "Name, phone number, and issue description are required"}), 400
    try:
        result = db.submit_issue(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/issues", methods=["GET"])
def get_admin_issues():
    """Admin endpoint to retrieve all devotee issues."""
    try:
        issues = db.get_all_issues()
        return jsonify(issues)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/issues/<int:issue_id>/status", methods=["PUT"])
def update_issue_status(issue_id):
    """Admin endpoint to update issue status and optional notes."""
    data = request.get_json() or {}
    status = data.get("status")
    notes = data.get("notes")
    if not status:
        return jsonify({"error": "Status is required"}), 400
    try:
        db.update_issue_status(issue_id, status, notes)
        return jsonify({"success": True, "issue_id": issue_id, "status": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/google", methods=["POST"])
def google_auth():
    """Authenticates or signs in user via Google credential token."""
    data = request.get_json() or {}
    credential = data.get("credential")
    email = data.get("email")
    name = data.get("name")

    if credential and not email:
        try:
            import base64
            parts = credential.split(".")
            if len(parts) >= 2:
                payload_part = parts[1]
                payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
                decoded_bytes = base64.urlsafe_b64decode(payload_part)
                token_data = json.loads(decoded_bytes.decode("utf-8"))
                email = token_data.get("email")
                name = token_data.get("name") or token_data.get("given_name")
        except Exception as ex:
            logging.warning(f"Could not decode Google JWT token: {ex}")

    if not email:
        return jsonify({"error": "Valid Google account email or credential required"}), 400

    try:
        user = db.get_or_create_google_user({"email": email, "name": name or email.split("@")[0]})
        return jsonify({"success": True, "user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/youtube/feed", methods=["GET"])
def get_youtube_feed():
    """Returns real-time Rushivani YouTube videos and shorts with automatic thumbnails and clickable links."""
    try:
        feed_data = youtube_service.fetch_rushivani_feed()
        return jsonify(feed_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/youtube/posts", methods=["GET"])
def get_youtube_posts():
    """Returns real-time Rushivani YouTube community posts with automatic images and clickable links."""
    try:
        posts_data = youtube_service.fetch_rushivani_posts()
        return jsonify(posts_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"Starting Divine Products E-Commerce Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
