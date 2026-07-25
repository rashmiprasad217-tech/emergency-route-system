import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask application key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-development-secret-key-12345')
    
    # MongoDB Database configuration
    # Can connect to a local server or a free MongoDB Atlas cloud cluster
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/emergency_route_system')
    
    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
