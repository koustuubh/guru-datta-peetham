import os
import sqlite3
import logging
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("divine_db")

# Optional oracledb import
HAS_ORACLEDB = False
try:
    import oracledb
    HAS_ORACLEDB = True
except ImportError:
    logger.warning("python-oracledb is not installed. Running in mock/SQLite fallback mode.")

ORACLE_USER = os.getenv("ORACLE_USER", "admin")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE_NAME = os.getenv("ORACLE_SERVICE_NAME", "FREEPDB1")
ORACLE_CONNECT_STRING = os.getenv("ORACLE_CONNECT_STRING", "")
AUTO_FALLBACK_SQLITE = os.getenv("AUTO_FALLBACK_SQLITE", "true").lower() in ("true", "1", "yes")

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "divine_store.db")

# Global driver state
DB_ENGINE = "uninitialized"  # 'oracle' or 'sqlite'
DB_ERROR_MESSAGE = ""
_oracle_pool = None

def init_oracle_connection():
    """Attempt to connect to Oracle DBMS and create connection pool."""
    global DB_ENGINE, DB_ERROR_MESSAGE, _oracle_pool
    if not HAS_ORACLEDB:
        DB_ENGINE = "sqlite"
        DB_ERROR_MESSAGE = "python-oracledb package not installed."
        return False

    try:
        # Build connect string / DSN
        dsn = ORACLE_CONNECT_STRING
        if not dsn:
            dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE_NAME}"

        logger.info(f"Attempting Oracle DB connection to: {dsn} as user: {ORACLE_USER}")
        
        # Test connection (Thin Mode is default in modern python-oracledb)
        conn = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=dsn
        )
        conn.close()

        # Create connection pool
        _oracle_pool = oracledb.create_pool(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=dsn,
            min=1,
            max=5,
            increment=1
        )
        DB_ENGINE = "oracle"
        DB_ERROR_MESSAGE = ""
        logger.info("Successfully connected to Oracle Database!")
        _ensure_oracle_tables()
        return True
    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Oracle DB connection failed: {err_msg}")
        DB_ERROR_MESSAGE = err_msg
        if AUTO_FALLBACK_SQLITE:
            logger.info("Falling back to local SQLite database for instant full-feature testing.")
            DB_ENGINE = "sqlite"
            _init_sqlite_db()
            return True
        else:
            DB_ENGINE = "error"
            return False

def _ensure_oracle_tables():
    """Verifies or initializes tables in Oracle DBMS."""
    conn = _oracle_pool.acquire()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'PRODUCTS'")
        res = cursor.fetchone()
        if res and res[0] == 0:
            logger.info("Oracle tables do not exist yet. Please run schema.sql or execute setup.")
    except Exception as e:
        logger.error(f"Error checking Oracle tables: {e}")
    finally:
        cursor.close()
        _oracle_pool.release(conn)

def _init_sqlite_db():
    """Initializes local SQLite database with full divine schema and seed items."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        slug TEXT NOT NULL UNIQUE,
        description TEXT,
        icon TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        slug TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        original_price REAL,
        stock_quantity INTEGER DEFAULT 0 NOT NULL,
        rating REAL DEFAULT 5.0,
        review_count INTEGER DEFAULT 0,
        image_url TEXT,
        is_featured INTEGER DEFAULT 0,
        tag TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        has_whatsapp INTEGER DEFAULT 1,
        utr_number TEXT,
        shipping_address TEXT NOT NULL,
        payment_method TEXT DEFAULT 'UPI' NOT NULL,
        payment_status TEXT DEFAULT 'PENDING_VERIFICATION' NOT NULL,
        total_amount REAL NOT NULL,
        order_status TEXT DEFAULT 'CONFIRMED' NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS issues (
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        devotee_name TEXT NOT NULL,
        email TEXT,
        phone TEXT NOT NULL,
        has_whatsapp INTEGER DEFAULT 1,
        order_number TEXT,
        issue_type TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN' NOT NULL,
        admin_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Safe migrations for existing sqlite databases
    for migration in [
        "ALTER TABLE orders ADD COLUMN has_whatsapp INTEGER DEFAULT 1",
        "ALTER TABLE orders ADD COLUMN utr_number TEXT",
        "ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'PENDING_VERIFICATION'"
    ]:
        try:
            cursor.execute(migration)
        except Exception:
            pass

    # Seed data if empty
    cursor.execute("SELECT count(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO categories (category_id, category_name, slug, description, icon) VALUES (?, ?, ?, ?, ?)
        """, [
            (1, 'Dattatreya Murtis', 'dattatreya-murtis', 'Consecrated Trimurti idols with 4 dogs & Kamadhenu', 'om'),
            (2, 'Sacred Padukas & Yantras', 'padukas-yantras', 'Holy Charan Padukas and energized Dattatreya Yantras', 'award'),
            (3, 'Audumbar & Malas', 'malas', 'Original Audumbar tree wood beads & energized malas', 'gem'),
            (4, 'Guru Charitra & Scriptures', 'scriptures', 'Complete Guru Charitra pothi & Datta stotras', 'book'),
            (5, 'Datta Pooja Essentials', 'pooja-essentials', 'Girnar Ashta-Gandha chandan, holy vibhuti, and aarti lamps', 'fire')
        ])

    cursor.execute("SELECT count(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO products (product_id, category_id, name, slug, description, price, original_price, stock_quantity, rating, review_count, image_url, is_featured, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 1, 'Pure Brass Lord Dattatreya Idol with Arch (7 inch)', 'brass-lord-dattatreya-idol-7in', 'Exquisite 3-faced Lord Dattatreya (Brahma, Vishnu, Maheshwara) surrounded by 4 sacred Vedas as dogs and Kamadhenu. Consecrated for peace and obstacle removal.', 2499.00, 3200.00, 20, 5.0, 184, 'dattatreya', 1, 'SACRED'),
            (2, 2, 'Consecrated Brass Datta Charan Paduka (Holy Feet)', 'brass-datta-charan-paduka', 'Heavy solid brass lotus footprints of Lord Dattatreya embossed with auspicious Ashtamangala signs. Ideal for daily Abhishekam.', 1299.00, 1750.00, 35, 4.9, 142, 'paduka', 1, 'HOLY FEET'),
            (3, 3, 'Original Karungali Mala (108 Ebony Wood Beads, 8mm)', 'original-karungali-mala-108-beads', 'Authentic black ebony wood (Karungali) energized at the Peetham. Shields against negative energies, pacifies Mars dosha, and brings success and strength.', 1499.00, 1999.00, 40, 5.0, 246, 'karungali', 1, 'BESTSELLER'),
            (4, 3, 'Natural Black Hakik Mala (108 Beads with Silver Cap)', 'natural-black-hakik-mala-108-beads', 'Pure certified Kala Akik (Black Agate) energized with Datta Kavacham. Shields from evil eye (Drishti), calms anxiety, and balances Rahu-Shani influences.', 899.00, 1250.00, 45, 4.9, 182, 'hakik', 1, 'EVIL EYE REMEDY'),
            (5, 3, 'Energized Red Hakik Mala (Lal Akik, 108 Beads)', 'energized-red-hakik-mala-108-beads', 'Natural Red Agate beads strung on durable sacred thread. Enhances physical vitality, courage, willpower, and root chakra balance.', 950.00, 1300.00, 30, 4.8, 94, 'hakik', 0, 'VITALITY'),
            (6, 3, 'Lab-Certified 5-Mukhi Nepali Rudraksha Mala (108 Beads)', 'lab-certified-5-mukhi-nepali-rudraksha-mala', 'Premium authentic 5-Mukhi Nepali Rudraksha beads with silver capping. Ideal for daily mantra japa, mental peace, and spiritual focus.', 1299.00, 1800.00, 50, 5.0, 312, 'rudraksha_mala', 1, 'CERTIFIED'),
            (7, 3, 'Rare Natural 1-Mukhi (Ek Mukhi) Rudraksha in Pure Silver', 'rare-1-mukhi-rudraksha-pure-silver', 'Exceedingly rare cashew-shaped 1-Mukhi Rudraksha mounted in pure 925 silver capping. Awakens higher spiritual consciousness and bestows Lord Shiva grace.', 3499.00, 4500.00, 10, 5.0, 88, 'ek_mukhi', 1, 'RARE / SHIVA'),
            (8, 3, 'Sacred Gauri Shankar Rudraksha (Joined Shiva-Parvati)', 'sacred-gauri-shankar-rudraksha', 'Two naturally conjoined sacred Rudraksha beads representing Shiva and Shakti. Brings family unity, marital harmony, and peace.', 2999.00, 3800.00, 15, 4.9, 74, 'gauri_shankar', 1, 'HARMONY'),
            (9, 3, 'Authentic Audumbar Wood Japa Mala (108 Beads)', 'authentic-audumbar-wood-japa-mala', 'Natural beads crafted from the holy Audumbara (Fig) tree beloved by Lord Dattatreya. Energized with Digambara Datta mantra.', 699.00, 950.00, 50, 4.9, 210, 'mala', 1, 'ENERGIZED'),
            (10, 4, 'Shri Guru Charitra Sacred Pothi (Hardcover)', 'shri-guru-charitra-sacred-pothi', 'The divine scripture detailing the leelas of Lord Dattatreya, Sripada Srivallabha, and Sri Narasimha Saraswati. Includes complete daily parayana rules.', 850.00, 1100.00, 40, 5.0, 320, 'charitra', 1, 'MUST READ'),
            (11, 2, 'Energized Copper Dattatreya Mahayantra (3x3 inch)', 'copper-dattatreya-mahayantra', 'Pure copper sacred geometric yantra blessed by Vedic priests to magnetize divine wisdom, spiritual protection, and family harmony.', 799.00, 1050.00, 30, 4.8, 98, 'yantra', 0, 'PROTECTION'),
            (12, 5, 'Girnar Ashta-Gandha Pure Sandalwood Chandan (100g)', 'girnar-ashta-gandha-chandan', 'Original saffron and sandalwood paste prepared according to ancient temple recipes for Lord Dattatreya tilak and pooja.', 349.00, 450.00, 100, 4.9, 115, 'chandan', 0, 'FRAGRANT'),
            (13, 5, 'Akhand Jyot Solid Brass Aarti Diya with Cover', 'akhand-jyot-solid-brass-aarti-diya', 'Heavy brass oil lamp with wind-guard designed for uninterrupted 24-hour holy flame during Guru Datta worship.', 1150.00, 1500.00, 25, 4.8, 88, 'diya', 0, 'TEMPLE GRADE'),
            (14, 5, 'Sacred Vibhuti (Holy Ash from Datta Dhuni, 200g)', 'sacred-vibhuti-datta-dhuni', 'Sanctified Bhasma taken from the continuous sacred fire (Dhuni) of Datta Kshetra. Dispels negativity and brings mental calm.', 249.00, 350.00, 120, 5.0, 175, 'vibhuti', 0, 'SANCTIFIED')
        ])

    conn.commit()
    conn.close()
    logger.info("SQLite database initialized successfully with seed data.")

def get_db_cursor():
    """Returns a tuple (conn, cursor) according to DB_ENGINE."""
    if DB_ENGINE == "oracle":
        conn = _oracle_pool.acquire()
        cursor = conn.cursor()
        return conn, cursor, "oracle"
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        return conn, cursor, "sqlite"

def close_db(conn, cursor, engine_type):
    """Safely closes / returns connection."""
    try:
        if cursor:
            cursor.close()
        if conn:
            if engine_type == "oracle":
                _oracle_pool.release(conn)
            else:
                conn.close()
    except Exception as e:
        logger.error(f"Error closing DB connection: {e}")

def dict_from_row(cursor, row):
    """Converts a cursor row to a python dict using column descriptions."""
    if isinstance(row, sqlite3.Row):
        return dict(row)
    if not row or not cursor.description:
        return {}
    cols = [col[0].lower() for col in cursor.description]
    return dict(zip(cols, row))

# --- Public API methods ---

def get_categories():
    """Fetches all categories along with count of available products."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        SELECT c.category_id, c.category_name, c.slug, c.description, c.icon,
               COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        GROUP BY c.category_id, c.category_name, c.slug, c.description, c.icon
        ORDER BY c.category_id
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict_from_row(cursor, r) for r in rows]
    finally:
        close_db(conn, cursor, engine)

def get_products(category_id=None, search=None, featured_only=False):
    """Fetches products with optional category, search, and featured filters."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        SELECT p.product_id, p.category_id, p.name, p.slug, p.description,
               p.price, p.original_price, p.stock_quantity, p.rating,
               p.review_count, p.image_url, p.is_featured, p.tag, p.created_at,
               c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE 1=1
        """
        params = {}
        if category_id:
            sql += " AND p.category_id = :cat_id"
            params["cat_id"] = int(category_id)
        if search:
            sql += " AND (LOWER(p.name) LIKE :search OR LOWER(p.description) LIKE :search)"
            params["search"] = f"%{search.strip().lower()}%"
        if featured_only:
            sql += " AND p.is_featured = 1"

        sql += " ORDER BY p.is_featured DESC, p.product_id ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict_from_row(cursor, r) for r in rows]
    finally:
        close_db(conn, cursor, engine)

def get_product(product_id):
    """Fetches a single product by ID."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        SELECT p.product_id, p.category_id, p.name, p.slug, p.description,
               p.price, p.original_price, p.stock_quantity, p.rating,
               p.review_count, p.image_url, p.is_featured, p.tag, p.created_at,
               c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = :p_id
        """
        cursor.execute(sql, {"p_id": int(product_id)})
        row = cursor.fetchone()
        return dict_from_row(cursor, row) if row else None
    finally:
        close_db(conn, cursor, engine)

def create_product(data):
    """Creates a new divine product in Oracle / DB."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        INSERT INTO products (
            category_id, name, slug, description, price,
            original_price, stock_quantity, rating, review_count,
            image_url, is_featured, tag
        ) VALUES (
            :cat_id, :name, :slug, :desc, :price,
            :orig_price, :stock, :rating, :rev_count,
            :img, :featured, :tag
        )
        """
        slug = data["name"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "")[:180]
        params = {
            "cat_id": int(data["category_id"]),
            "name": data["name"],
            "slug": slug,
            "desc": data.get("description", ""),
            "price": float(data["price"]),
            "orig_price": float(data.get("original_price") or data["price"]),
            "stock": int(data.get("stock_quantity", 10)),
            "rating": float(data.get("rating", 5.0)),
            "rev_count": int(data.get("review_count", 1)),
            "img": data.get("image_url", "default_divine"),
            "featured": 1 if data.get("is_featured") else 0,
            "tag": data.get("tag", "NEW")
        }
        cursor.execute(sql, params)
        conn.commit()

        if engine == "sqlite":
            new_id = cursor.lastrowid
        else:
            # Query last generated ID in Oracle or use RETURNING
            cursor.execute("SELECT MAX(product_id) FROM products")
            new_id = cursor.fetchone()[0]
            
        return get_product(new_id)
    finally:
        close_db(conn, cursor, engine)

def update_product(product_id, data):
    """Updates product information or inventory."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        UPDATE products
        SET name = :name,
            category_id = :cat_id,
            description = :desc,
            price = :price,
            stock_quantity = :stock,
            is_featured = :featured,
            tag = :tag
        WHERE product_id = :p_id
        """
        params = {
            "p_id": int(product_id),
            "name": data["name"],
            "cat_id": int(data["category_id"]),
            "desc": data.get("description", ""),
            "price": float(data["price"]),
            "stock": int(data.get("stock_quantity", 0)),
            "featured": 1 if data.get("is_featured") else 0,
            "tag": data.get("tag", "")
        }
        cursor.execute(sql, params)
        conn.commit()
        return get_product(product_id)
    finally:
        close_db(conn, cursor, engine)

def delete_product(product_id):
    """Deletes a product by ID."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("DELETE FROM products WHERE product_id = :p_id", {"p_id": int(product_id)})
        conn.commit()
        return True
    finally:
        close_db(conn, cursor, engine)

def create_order(order_info, cart_items):
    """Creates a new customer order and associated order items atomically."""
    conn, cursor, engine = get_db_cursor()
    try:
        order_number = "DIV-" + datetime.now().strftime("%Y%m%d%H%M%S") + f"-{random.randint(100, 999)}"
        total_amount = sum(float(item["price"]) * int(item["quantity"]) for item in cart_items)
        
        has_whatsapp = 1 if order_info.get("has_whatsapp", True) else 0
        utr_number = (order_info.get("utr_number") or "").strip()
        payment_status = "PAID_VERIFIED" if (utr_number and len(utr_number) >= 6) else order_info.get("payment_status", "PENDING_VERIFICATION")

        # Insert order
        sql_order = """
        INSERT INTO orders (
            order_number, customer_name, customer_email, customer_phone,
            has_whatsapp, utr_number, shipping_address, payment_method,
            payment_status, total_amount, order_status
        ) VALUES (
            :ord_no, :c_name, :c_email, :c_phone,
            :wa, :utr, :ship_addr, :pay_method,
            :p_status, :total, 'CONFIRMED'
        )
        """
        params_order = {
            "ord_no": order_number,
            "c_name": order_info["customer_name"],
            "c_email": order_info["customer_email"],
            "c_phone": order_info["customer_phone"],
            "wa": has_whatsapp,
            "utr": utr_number or None,
            "ship_addr": order_info["shipping_address"],
            "pay_method": order_info.get("payment_method", "UPI"),
            "p_status": payment_status,
            "total": total_amount
        }
        cursor.execute(sql_order, params_order)

        if engine == "sqlite":
            order_id = cursor.lastrowid
        else:
            cursor.execute("SELECT MAX(order_id) FROM orders")
            order_id = cursor.fetchone()[0]

        # Insert order items and deduct stock
        for item in cart_items:
            subtotal = float(item["price"]) * int(item["quantity"])
            sql_item = """
            INSERT INTO order_items (
                order_id, product_id, product_name, quantity, unit_price, subtotal
            ) VALUES (
                :o_id, :p_id, :p_name, :qty, :unit_p, :sub
            )
            """
            cursor.execute(sql_item, {
                "o_id": order_id,
                "p_id": int(item["product_id"]),
                "p_name": item["name"],
                "qty": int(item["quantity"]),
                "unit_p": float(item["price"]),
                "sub": subtotal
            })

            # Deduct stock
            cursor.execute("""
            UPDATE products
            SET stock_quantity = MAX(0, stock_quantity - :qty)
            WHERE product_id = :p_id
            """, {"qty": int(item["quantity"]), "p_id": int(item["product_id"])})

        conn.commit()
        return {
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount,
            "order_status": "CONFIRMED",
            "payment_status": payment_status,
            "has_whatsapp": has_whatsapp,
            "utr_number": utr_number,
            "items_count": len(cart_items)
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn, cursor, engine)

def get_orders():
    """Retrieves recent orders with their item count."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        SELECT o.order_id, o.order_number, o.customer_name, o.customer_email,
               o.customer_phone, o.has_whatsapp, o.utr_number, o.shipping_address,
               o.payment_method, o.payment_status, o.total_amount, o.order_status,
               o.created_at,
               COUNT(oi.order_item_id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id, o.order_number, o.customer_name, o.customer_email,
                 o.customer_phone, o.has_whatsapp, o.utr_number, o.shipping_address,
                 o.payment_method, o.payment_status, o.total_amount, o.order_status,
                 o.created_at
        ORDER BY o.order_id DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict_from_row(cursor, r) for r in rows]
    finally:
        close_db(conn, cursor, engine)

def update_order_status(order_id, new_status):
    """Updates status of an order in the database."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("UPDATE orders SET order_status = :status WHERE order_id = :o_id", {
            "status": new_status,
            "o_id": int(order_id)
        })
        conn.commit()
        return True
    finally:
        close_db(conn, cursor, engine)

def update_order_payment(order_id, payment_status, utr_number=None):
    """Admin updates transaction verification status and optional UTR."""
    conn, cursor, engine = get_db_cursor()
    try:
        if utr_number:
            cursor.execute("""
            UPDATE orders
            SET payment_status = :status, utr_number = :utr
            WHERE order_id = :o_id
            """, {
                "status": payment_status,
                "utr": utr_number,
                "o_id": int(order_id)
            })
        else:
            cursor.execute("""
            UPDATE orders
            SET payment_status = :status
            WHERE order_id = :o_id
            """, {
                "status": payment_status,
                "o_id": int(order_id)
            })
        conn.commit()
        return True
    finally:
        close_db(conn, cursor, engine)

def update_product_price(product_id, new_price, stock=None):
    """Admin updates rate and optional stock quantity."""
    conn, cursor, engine = get_db_cursor()
    try:
        if stock is not None:
            cursor.execute("""
            UPDATE products
            SET price = :p, stock_quantity = :s
            WHERE product_id = :id
            """, {
                "p": float(new_price),
                "s": int(stock),
                "id": int(product_id)
            })
        else:
            cursor.execute("""
            UPDATE products
            SET price = :p
            WHERE product_id = :id
            """, {
                "p": float(new_price),
                "id": int(product_id)
            })
        conn.commit()
        return get_product(product_id)
    finally:
        close_db(conn, cursor, engine)

def submit_issue(data):
    """Records a new devotee issue / helpdesk ticket."""
    conn, cursor, engine = get_db_cursor()
    try:
        sql = """
        INSERT INTO issues (
            devotee_name, email, phone, has_whatsapp,
            order_number, issue_type, description, status
        ) VALUES (
            :name, :email, :phone, :wa,
            :ord_no, :type, :desc, 'OPEN'
        )
        """
        params = {
            "name": data["devotee_name"].strip(),
            "email": (data.get("email") or "").strip(),
            "phone": data["phone"].strip(),
            "wa": 1 if data.get("has_whatsapp", True) else 0,
            "ord_no": (data.get("order_number") or "").strip(),
            "type": (data.get("issue_type") or "General Inquiry").strip(),
            "desc": data["description"].strip()
        }
        cursor.execute(sql, params)
        conn.commit()

        if engine == "sqlite":
            issue_id = cursor.lastrowid
        else:
            cursor.execute("SELECT MAX(issue_id) FROM issues")
            issue_id = cursor.fetchone()[0]

        return {
            "issue_id": issue_id,
            "devotee_name": params["name"],
            "status": "OPEN",
            "message": "Your issue has been recorded at Guru Datta Peetham. We will reach out shortly."
        }
    finally:
        close_db(conn, cursor, engine)

def get_all_issues():
    """Retrieves all devotee support issues for the admin dashboard."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("""
        SELECT issue_id, devotee_name, email, phone, has_whatsapp,
               order_number, issue_type, description, status, admin_notes, created_at
        FROM issues
        ORDER BY issue_id DESC
        """)
        rows = cursor.fetchall()
        return [dict_from_row(cursor, r) for r in rows]
    finally:
        close_db(conn, cursor, engine)

def update_issue_status(issue_id, status, notes=None):
    """Admin updates issue status (e.g. RESOLVED) and notes."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("""
        UPDATE issues
        SET status = :status, admin_notes = COALESCE(:notes, admin_notes)
        WHERE issue_id = :id
        """, {
            "status": status,
            "notes": notes,
            "id": int(issue_id)
        })
        conn.commit()
        return True
    finally:
        close_db(conn, cursor, engine)

def get_or_create_google_user(google_info):
    """Authenticates or registers a user via Google Sign-In."""
    email = (google_info.get("email") or "").strip().lower()
    name = (google_info.get("name") or email.split("@")[0]).strip()
    if not email:
        raise ValueError("Google account email is required")

    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("SELECT user_id, username, full_name, role, phone, email FROM users WHERE LOWER(email) = :em", {"em": email})
        row = cursor.fetchone()
        if row:
            return dict_from_row(cursor, row)

        username = email.split("@")[0].lower() + f"_{random.randint(100, 999)}"
        cursor.execute("""
        INSERT INTO users (username, password, full_name, phone, email, role)
        VALUES (:u, 'google_oauth', :fn, '', :em, 'user')
        """, {
            "u": username,
            "fn": name,
            "em": email
        })
        conn.commit()

        if engine == "sqlite":
            u_id = cursor.lastrowid
        else:
            cursor.execute("SELECT MAX(user_id) FROM users")
            u_id = cursor.fetchone()[0]

        return {
            "user_id": u_id,
            "username": username,
            "full_name": name,
            "email": email,
            "role": "user"
        }
    finally:
        close_db(conn, cursor, engine)

def authenticate_user(username, password):
    """Validates user or admin credentials."""
    username = (username or '').strip().lower()
    password = (password or '').strip()

    # Master Admin login for Guruji / Temple Admin
    if username in ('admin', 'guruji', 'datta') and password in ('datta123', 'admin123', 'datta'):
        return {
            "user_id": 1,
            "username": "admin",
            "full_name": "Guruji Dr. Shanmukha Srinivas (Admin)",
            "role": "admin"
        }

    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("SELECT user_id, username, full_name, role, phone, email FROM users WHERE LOWER(username) = :u AND password = :p", {
            "u": username,
            "p": password
        })
        row = cursor.fetchone()
        if row:
            return dict_from_row(cursor, row)
        return None
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return None
    finally:
        close_db(conn, cursor, engine)

def register_user(username, password, full_name, phone="", email=""):
    """Registers a new devotee user."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("""
        INSERT INTO users (username, password, full_name, phone, email, role)
        VALUES (:u, :p, :fn, :ph, :em, 'user')
        """, {
            "u": username.strip().lower(),
            "p": password.strip(),
            "fn": full_name.strip(),
            "ph": phone.strip(),
            "em": email.strip()
        })
        conn.commit()
        return {
            "username": username,
            "full_name": full_name,
            "role": "user"
        }
    except Exception as e:
        raise e
    finally:
        close_db(conn, cursor, engine)

def get_health_status():
    """Returns database health, active engine, and table counts."""
    conn, cursor, engine = get_db_cursor()
    try:
        cursor.execute("SELECT count(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM orders")
        order_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM categories")
        category_count = cursor.fetchone()[0]

        return {
            "status": "healthy",
            "database_engine": "Oracle DBMS" if engine == "oracle" else "SQLite (Fallback / Demo)",
            "engine_type": engine,
            "oracle_target": f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE_NAME}",
            "oracle_user": ORACLE_USER,
            "oracle_error": DB_ERROR_MESSAGE if engine != "oracle" else None,
            "counts": {
                "categories": category_count,
                "products": product_count,
                "orders": order_count
            }
        }
    finally:
        close_db(conn, cursor, engine)

# Auto-initialize on module load
init_oracle_connection()
