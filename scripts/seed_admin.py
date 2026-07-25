import os
import sys
import pymongo
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Add parent directory to system path to import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def seed():
    print("Seeding default admin credentials to MongoDB...")
    client = None
    try:
        client = pymongo.MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
        try:
            db = client.get_default_database()
            if db is None or db.name == 'admin':
                db = client['emergency_route_system']
        except Exception:
            db = client['emergency_route_system']
            
        # Ensure connection
        client.server_info()
        
        # Secure password hash
        hashed_password = generate_password_hash("admin123")
        
        # Reset and insert default admin
        db.admins.delete_many({"username": "admin"})
        db.admins.insert_one({
            "username": "admin",
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
        })
        print("[SUCCESS] Seeding complete! Credentials are:")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as err:
        print(f"[ERROR] Seeding failed: {err}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    seed()
