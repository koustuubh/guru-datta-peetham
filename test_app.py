import unittest
import json
import os
import sys

# Ensure local app path is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import db

class DivineStoreTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_index_page(self):
        """Test homepage renders successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"GURU DATTA PEETHAM", response.data)
        self.assertIn(b"Lord Dattatreya", response.data)

    def test_02_health_endpoint(self):
        """Test health diagnostics."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("database_engine", data)
        self.assertGreater(data["counts"]["categories"], 0)
        self.assertGreater(data["counts"]["products"], 0)

    def test_03_get_categories(self):
        """Test fetching categories with counts."""
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        categories = response.get_json()
        self.assertIsInstance(categories, list)
        self.assertGreaterEqual(len(categories), 5)
        # Check essential categories exist
        cat_names = [c["category_name"] for c in categories]
        self.assertTrue(any("Dattatreya" in name for name in cat_names))
        self.assertTrue(any("Malas" in name for name in cat_names))

    def test_04_get_products(self):
        """Test product filtering and listing."""
        # All products
        res = self.client.get("/api/products")
        self.assertEqual(res.status_code, 200)
        products = res.get_json()
        self.assertGreaterEqual(len(products), 8)

        # Filter by search
        res_search = self.client.get("/api/products?search=Dattatreya")
        self.assertEqual(res_search.status_code, 200)
        search_prods = res_search.get_json()
        self.assertGreaterEqual(len(search_prods), 1)
        self.assertIn("Dattatreya", search_prods[0]["name"])

        # Filter by featured
        res_feat = self.client.get("/api/products?featured=true")
        self.assertEqual(res_feat.status_code, 200)
        feat_prods = res_feat.get_json()
        self.assertTrue(all(p["is_featured"] == 1 for p in feat_prods))

    def test_05_product_crud_lifecycle(self):
        """Test adding, retrieving, updating, and deleting a product."""
        # 1. Create
        payload = {
            "name": "Energized Sri Meru Chakra Brass (4 inch)",
            "category_id": 4,
            "price": 2899.00,
            "original_price": 3500.00,
            "stock_quantity": 15,
            "tag": "DIVINE TEST",
            "description": "Powerful 3D sacred geometry Sri Meru Chakra cast in high quality brass.",
            "is_featured": 1
        }
        res_create = self.client.post("/api/products", json=payload)
        self.assertEqual(res_create.status_code, 201)
        created = res_create.get_json()
        prod_id = created["product_id"]
        self.assertEqual(created["name"], payload["name"])

        # 2. Read
        res_read = self.client.get(f"/api/products/{prod_id}")
        self.assertEqual(res_read.status_code, 200)
        self.assertEqual(res_read.get_json()["name"], payload["name"])

        # 3. Update
        update_payload = {
            "name": "Energized Sri Meru Chakra Brass (Updated Edition)",
            "category_id": 4,
            "price": 2999.00,
            "stock_quantity": 25,
            "tag": "UPDATED",
            "is_featured": 0
        }
        res_update = self.client.put(f"/api/products/{prod_id}", json=update_payload)
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.get_json()
        self.assertEqual(updated["name"], update_payload["name"])
        self.assertEqual(updated["stock_quantity"], 25)

        # 4. Delete
        res_delete = self.client.delete(f"/api/products/{prod_id}")
        self.assertEqual(res_delete.status_code, 200)

        # Verify Deleted
        res_check = self.client.get(f"/api/products/{prod_id}")
        self.assertEqual(res_check.status_code, 404)

    def test_06_place_and_retrieve_order(self):
        """Test order placement and inventory reduction."""
        # Ensure product 1 has ample stock for test
        self.client.put("/api/products/1/price", json={"price": 2499.00, "stock_quantity": 25})
        prod_before = self.client.get("/api/products/1").get_json()
        stock_before = prod_before["stock_quantity"]

        order_payload = {
            "customer": {
                "customer_name": "Devotee Ananya Sharma",
                "customer_email": "ananya@example.com",
                "customer_phone": "9876543210",
                "shipping_address": "Plot 42, Temple View Enclave, Varanasi, UP 221001",
                "payment_method": "UPI"
            },
            "items": [
                {
                    "product_id": 1,
                    "name": prod_before["name"],
                    "price": prod_before["price"],
                    "quantity": 2
                }
            ]
        }

        res_order = self.client.post("/api/orders", json=order_payload)
        self.assertEqual(res_order.status_code, 201)
        order_res = res_order.get_json()
        self.assertIn("DIV-", order_res["order_number"])
        self.assertEqual(order_res["order_status"], "CONFIRMED")

        # Verify stock was deducted
        prod_after = self.client.get("/api/products/1").get_json()
        self.assertEqual(prod_after["stock_quantity"], stock_before - 2)

        # Verify order appears in orders list
        res_orders = self.client.get("/api/orders")
        self.assertEqual(res_orders.status_code, 200)
        orders = res_orders.get_json()
        self.assertTrue(any(o["order_number"] == order_res["order_number"] for o in orders))

    def test_07_auth_and_order_status_update(self):
        """Test admin login and order status updating."""
        # 1. Admin login valid
        login_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "datta123"})
        self.assertEqual(login_res.status_code, 200)
        user_data = login_res.get_json()
        self.assertTrue(user_data["success"])
        self.assertEqual(user_data["user"]["role"], "admin")

        # 2. Invalid login
        invalid_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(invalid_res.status_code, 401)

        # 3. Create test order to update status
        order_payload = {
            "customer": {
                "customer_name": "Srinivas Rao",
                "customer_email": "srinivas@example.com",
                "customer_phone": "9988776655",
                "shipping_address": "Hyderabad, Telangana",
                "payment_method": "UPI"
            },
            "items": [{"product_id": 1, "name": "Test Item", "price": 1000, "quantity": 1}]
        }
        res_order = self.client.post("/api/orders", json=order_payload)
        self.assertEqual(res_order.status_code, 201)
        created_order = res_order.get_json()
        order_id = created_order["order_id"]

        # 4. Update status to DISPATCHED
        res_status = self.client.put(f"/api/admin/orders/{order_id}/status", json={"status": "DISPATCHED"})
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.get_json()
        self.assertEqual(status_data["status"], "DISPATCHED")

        # 5. Check in orders list
        orders = self.client.get("/api/orders").get_json()
        target = next(o for o in orders if o["order_id"] == order_id)
        self.assertEqual(target["order_status"], "DISPATCHED")

    def test_08_youtube_feed(self):
        """Test real-time YouTube video & shorts endpoint with automatic thumbnails."""
        res = self.client.get("/api/youtube/feed")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("shorts", data)
        self.assertIn("videos", data)
        self.assertGreaterEqual(len(data["shorts"]), 3)
        self.assertGreaterEqual(len(data["videos"]), 3)

        # Check thumbnail structure
        first_short = data["shorts"][0]
        self.assertTrue(first_short["thumbnail"].startswith("https://"))
        self.assertIn("ytimg.com", first_short["thumbnail"])
        self.assertTrue(first_short["url"].startswith("https://www.youtube.com/"))

        first_video = data["videos"][0]
        self.assertTrue(first_video["thumbnail"].startswith("https://"))
        self.assertTrue(first_video["url"].startswith("https://www.youtube.com/"))

    def test_09_youtube_posts(self):
        """Test real-time YouTube community posts endpoint with automatic images and links."""
        res = self.client.get("/api/youtube/posts")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("posts", data)
        self.assertGreaterEqual(len(data["posts"]), 3)

        first_post = data["posts"][0]
        self.assertIn("id", first_post)
        self.assertIn("url", first_post)
        self.assertTrue(first_post["url"].startswith("https://www.youtube.com/post/"))
        self.assertIn("content", first_post)
        self.assertGreater(len(first_post["content"]), 0)
        self.assertIn("images", first_post)
        self.assertIsInstance(first_post["images"], list)
        if first_post["images"]:
            self.assertTrue(first_post["images"][0].startswith("https://"))

    def test_10_product_rate_update(self):
        """Test admin updating product rate/price."""
        res = self.client.put("/api/products/1/price", json={"price": 2799.00})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(float(data["price"]), 2799.00)

        # Verify in product fetch
        prod = self.client.get("/api/products/1").get_json()
        self.assertEqual(float(prod["price"]), 2799.00)

    def test_11_issue_submission_and_resolution(self):
        """Test devotee submitting issue and admin resolving it."""
        issue_payload = {
            "devotee_name": "Kalyan Ram",
            "phone": "9848012345",
            "has_whatsapp": 1,
            "email": "kalyan@example.com",
            "order_number": "DIV-TEST-999",
            "issue_type": "Order Tracking & Delivery",
            "description": "Please confirm if Karungali mala was dispatched today."
        }
        res_sub = self.client.post("/api/issues", json=issue_payload)
        self.assertEqual(res_sub.status_code, 201)
        sub_data = res_sub.get_json()
        issue_id = sub_data["issue_id"]
        self.assertEqual(sub_data["status"], "OPEN")

        # Admin gets all issues
        res_admin = self.client.get("/api/admin/issues")
        self.assertEqual(res_admin.status_code, 200)
        issues = res_admin.get_json()
        self.assertTrue(any(i["issue_id"] == issue_id for i in issues))

        # Admin resolves issue
        res_res = self.client.put(f"/api/admin/issues/{issue_id}/status", json={"status": "RESOLVED", "notes": "Tracking ID shared via WhatsApp"})
        self.assertEqual(res_res.status_code, 200)
        self.assertEqual(res_res.get_json()["status"], "RESOLVED")

    def test_12_order_with_utr_and_whatsapp(self):
        """Test order placement with UTR number, WhatsApp flag, and payment verification."""
        order_payload = {
            "customer": {
                "customer_name": "Suresh Kumar",
                "customer_email": "suresh@example.com",
                "customer_phone": "9949112233",
                "has_whatsapp": 1,
                "utr_number": "425612349876",
                "shipping_address": "Tirupati, Andhra Pradesh",
                "payment_method": "UPI"
            },
            "items": [{"product_id": 1, "name": "Lord Dattatreya Idol", "price": 2799.00, "quantity": 1}]
        }
        res = self.client.post("/api/orders", json=order_payload)
        self.assertEqual(res.status_code, 201)
        order_data = res.get_json()
        self.assertEqual(order_data["has_whatsapp"], 1)
        self.assertEqual(order_data["utr_number"], "425612349876")
        self.assertEqual(order_data["payment_status"], "PAID_VERIFIED")

        # Toggle payment status in admin
        order_id = order_data["order_id"]
        toggle_res = self.client.put(f"/api/admin/orders/{order_id}/payment", json={"payment_status": "PENDING_VERIFICATION"})
        self.assertEqual(toggle_res.status_code, 200)
        self.assertEqual(toggle_res.get_json()["payment_status"], "PENDING_VERIFICATION")

    def test_13_google_auth(self):
        """Test Google authentication endpoint."""
        res = self.client.post("/api/auth/google", json={"email": "devotee.datta@gmail.com", "name": "Datta Devotee"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], "devotee.datta@gmail.com")

if __name__ == "__main__":
    unittest.main()
