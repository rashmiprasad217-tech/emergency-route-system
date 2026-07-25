import os
import sys
import pymongo
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Add parent directory to system path to import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def create_admin():
    print("==================================================")
    print("Emergency Route System - MongoDB Admin Setup Utility")
    print("==================================================")
    
    # Prompt for admin credentials
    username = input("Enter admin username (default 'admin'): ").strip()
    if not username:
        username = 'admin'
        
    password = input("Enter admin password: ").strip()
    if not password:
        print("[ERROR] Password cannot be empty.")
        return
        
    confirm_password = input("Confirm admin password: ").strip()
    if password != confirm_password:
        print("[ERROR] Passwords do not match.")
        return
        
    # Securely hash the password
    hashed_password = generate_password_hash(password)
    
    client = None
    try:
        # Establish connection to MongoDB
        client = pymongo.MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Get database from URI, fallback to 'emergency_route_system' if not specified
        try:
            db = client.get_default_database()
            if db is None or db.name == 'admin':
                db = client['emergency_route_system']
        except Exception:
            db = client['emergency_route_system']
            
        # Test server connection
        client.server_info()
        
        # Check if username already exists in admins collection
        admin = db.admins.find_one({"username": username})
        
        if admin:
            confirm = input(f"Admin '{username}' already exists. Overwrite password? (y/n): ").strip().lower()
            if confirm == 'y':
                db.admins.update_one(
                    {"username": username},
                    {"$set": {"password": hashed_password}}
                )
                print(f"[SUCCESS] Admin '{username}' password updated successfully.")
            else:
                print("[INFO] Operation cancelled.")
        else:
            db.admins.insert_one({
                "username": username,
                "password": hashed_password,
                "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
            })
            print(f"[SUCCESS] Admin '{username}' created successfully.")
            
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"\n[MONGODB CONNECTION ERROR] Connection timed out: {err}")
        print("Please ensure your MongoDB server is running or that your MONGO_URI in .env is correct.")
    except Exception as err:
        print(f"\n[ERROR] An unexpected error occurred: {err}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    create_admin()
