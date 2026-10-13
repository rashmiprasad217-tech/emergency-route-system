import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

class Config:
    # Flask secret key for session encryption
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MongoDB Database configuration (defaults to local MongoDB server)
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/emergency_route_system')
    
    # Google Maps API Configuration (optional - app uses free Leaflet by default)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    # Session Configuration (configured for local HTTP development in VS Code)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
