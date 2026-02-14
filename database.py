import sqlite3

DB_NAME = "bloodbank.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # ================= USERS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        phone TEXT,
        address TEXT,
        gender TEXT,
        role TEXT,
        status TEXT
    )
    """)

    # ================= DONORS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        user_id INTEGER PRIMARY KEY,
        age INTEGER,
        weight REAL,
        blood_group TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # ================= CAMPS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS camps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        camp_date TEXT,
        camp_time TEXT,
        venue TEXT
    )
    """)

    # ================= DONATIONS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        units INTEGER,
        donation_date TEXT,
        result TEXT,
        FOREIGN KEY(donor_id) REFERENCES users(id)
    )
    """)

    # ================= HEALTH SCREENING =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_screening (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        hemoglobin REAL,
        blood_pressure TEXT,
        heart_rate INTEGER,
        temperature REAL,
        status TEXT,
        remarks TEXT,
        FOREIGN KEY(donor_id) REFERENCES users(id)
    )
    """)

    # ================= BLOOD STOCK =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_stock (
        blood_group TEXT PRIMARY KEY,
        units INTEGER
    )
    """)

    # ---------- NOTIFICATIONS ----------
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT,
        created_at TEXT,
        is_read INTEGER DEFAULT 0
    )
    """)
    
    # BLOOD REQUESTS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER,
        blood_group TEXT,
        units INTEGER,
        status TEXT DEFAULT 'Pending',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def create_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE role='admin'")
    admin = cur.fetchone()

    if not admin:
        cur.execute("""
        INSERT INTO users (name, email, password, role, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            "Admin",
            "admin@gmail.com",
            "admin123",
            "admin",
            "Approved"
        ))
        conn.commit()

    conn.close()


