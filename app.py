from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
import pymongo
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timezone
import re

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ==================================================
# DATABASE UTILITIES
# ==================================================
_mongo_client = None
_INDEXES_CREATED = False

def get_db():
    """Returns a connected MongoDB database instance, reusing connection pool and handling fallback."""
    global _mongo_client, _INDEXES_CREATED

    if _mongo_client is None:
        mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/emergency_route_system')
        
        # 1. Try configured URI
        try:
            if 'mongodb+srv://' in mongo_uri:
                _mongo_client = pymongo.MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=4000,
                    tls=True,
                    tlsAllowInvalidCertificates=True
                )
            else:
                _mongo_client = pymongo.MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=3000
                )
            # Verify connectivity
            _mongo_client.server_info()
        except Exception as primary_err:
            print(f"[WARNING] Primary MongoDB connection failed ({primary_err}). Falling back to local MongoDB...")
            try:
                # 2. Fallback to local MongoDB
                local_uri = 'mongodb://localhost:27017/emergency_route_system'
                _mongo_client = pymongo.MongoClient(
                    local_uri,
                    serverSelectionTimeoutMS=3000
                )
                _mongo_client.server_info()
            except Exception as local_err:
                print(f"[ERROR] Local MongoDB fallback also failed: {local_err}")
                # Re-raise primary error for standard Flask error handler
                raise primary_err

    try:
        db = _mongo_client.get_default_database()
        if db is None or db.name == 'admin':
            db = _mongo_client['emergency_route_system']
    except Exception:
        db = _mongo_client['emergency_route_system']
        
    # Ensure database indexes exist once per process worker
    if not _INDEXES_CREATED:
        try:
            db.users.create_index("email", unique=True)
            db.search_history.create_index("user_id")
            db.search_history.create_index("searched_at")
            db.route_history.create_index("user_id")
            db.route_history.create_index("created_at")
            _INDEXES_CREATED = True
        except Exception:
            pass

    return db

@app.context_processor
def inject_now():
    """Inject current datetime into all templates for footer and date rendering."""
    return {'datetime': datetime, 'current_year': datetime.now(timezone.utc).year}

@app.teardown_appcontext
def close_db(error):
    """PyMongo client maintains an internal connection pool across requests."""
    pass

@app.errorhandler(PyMongoError)
def handle_database_error(error):
    """Custom error handler to show MongoDB connection failures gracefully."""
    return render_template('db_error.html', error=error), 500


# ==================================================
# AUTHENTICATION DECORATORS
# ==================================================
def login_required(f):
    """Decorator to restrict access to authenticated users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict access to administrators only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Access denied. Please log in as Admin.", "danger")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================================================
# PUBLIC ROUTES
# ==================================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash("Please fill in all fields.", "danger")
        else:
            flash("Thank you for contacting us! We will get back to you shortly.", "success")
            return redirect(url_for('contact'))
            
    return render_template('contact.html')


# ==================================================
# USER AUTHENTICATION
# ==================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation checks
        if not name or not email or not phone or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address format.", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        try:
            db = get_db()
            
            # Check for duplicate email in users collection
            if db.users.find_one({"email": email}):
                flash("Email address is already registered.", "danger")
                return render_template('register.html')
                
            # Hash password securely
            hashed_pw = generate_password_hash(password)
            
            # Insert new user record
            db.users.insert_one({
                "name": name,
                "email": email,
                "phone": phone,
                "password": hashed_pw,
                "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
            })
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
            
        except PyMongoError as err:
            flash(f"Database error: {err}", "danger")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html')
            
        try:
            db = get_db()
            
            # Retrieve user document
            user = db.users.find_one({"email": email})
            
            if user and check_password_hash(user['password'], password):
                # Set session variables (store ObjectId as a clean string)
                session['user_id'] = str(user['_id'])
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password.", "danger")
                
        except PyMongoError as err:
            flash(f"Database error: {err}", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash("You have logged out successfully.", "info")
    return redirect(url_for('login'))


# ==================================================
# USER PANEL ROUTES
# ==================================================
@app.route('/dashboard')
@login_required
def dashboard():
    maps_key = app.config['GOOGLE_MAPS_API_KEY']
    return render_template('dashboard.html', maps_key=maps_key)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not name or not phone:
            flash("Name and Phone fields are required.", "danger")
        else:
            try:
                # Update basic info document
                db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"name": name, "phone": phone}}
                )
                session['user_name'] = name  # Update current session name
                flash("Profile updated successfully.", "success")
                
                # Update password if requested
                if new_password:
                    if new_password != confirm_password:
                        flash("New passwords do not match.", "danger")
                    else:
                        hashed_pw = generate_password_hash(new_password)
                        db.users.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {"password": hashed_pw}}
                        )
                        flash("Password updated successfully.", "success")
                        
                return redirect(url_for('profile'))
            except PyMongoError as err:
                flash(f"Database error: {err}", "danger")
                
    # Fetch latest user document to display
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template('profile.html', user=user)

@app.route('/search-history')
@login_required
def search_history():
    user_id = session['user_id']
    try:
        db = get_db()
        # Find search logs for this specific user
        history = list(db.search_history.find({"user_id": user_id}).sort("searched_at", pymongo.DESCENDING))
        
        # Inject standard string ID so Jinja template reads log.id
        for log in history:
            log['id'] = str(log['_id'])
            
        return render_template('search_history.html', history=history)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('search_history.html', history=[])

@app.route('/route-history')
@login_required
def route_history():
    user_id = session['user_id']
    try:
        db = get_db()
        # Find route logs for this specific user
        routes = list(db.route_history.find({"user_id": user_id}).sort("created_at", pymongo.DESCENDING))
        
        # Inject standard string ID so Jinja template reads route.id
        for route in routes:
            route['id'] = str(route['_id'])
            
        return render_template('route_history.html', routes=routes)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('route_history.html', routes=[])


# ==================================================
# AJAX / API ENDPOINTS
# ==================================================
@app.route('/api/save-search', methods=['POST'])
@login_required
def save_search():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    emergency_type = data.get('emergency_type')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not emergency_type or latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    try:
        db = get_db()
        # Insert log document
        db.search_history.insert_one({
            "user_id": session['user_id'],
            "emergency_type": emergency_type,
            "latitude": latitude,
            "longitude": longitude,
            "searched_at": datetime.now(timezone.utc).replace(tzinfo=None)
        })
        return jsonify({"status": "success", "message": "Search history saved"})
    except PyMongoError as err:
        return jsonify({"status": "error", "message": str(err)}), 500

@app.route('/api/save-route', methods=['POST'])
@login_required
def save_route():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    service_name = data.get('service_name')
    service_type = data.get('service_type')
    destination_address = data.get('destination_address')
    destination_latitude = data.get('destination_latitude')
    destination_longitude = data.get('destination_longitude')
    distance = data.get('distance')
    estimated_time = data.get('estimated_time')
    
    if not service_name or not service_type or not destination_address or destination_latitude is None or destination_longitude is None:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    try:
        db = get_db()
        # Insert route document
        db.route_history.insert_one({
            "user_id": session['user_id'],
            "service_name": service_name,
            "service_type": service_type,
            "destination_address": destination_address,
            "destination_latitude": destination_latitude,
            "destination_longitude": destination_longitude,
            "distance": distance,
            "estimated_time": estimated_time,
            "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
        })
        return jsonify({"status": "success", "message": "Route history saved"})
    except PyMongoError as err:
        return jsonify({"status": "error", "message": str(err)}), 500


# ==================================================
# ADMIN PANEL ROUTES
# ==================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('admin/login.html')
            
        try:
            db = get_db()
            admin = db.admins.find_one({"username": username})
            
            if admin and check_password_hash(admin['password'], password):
                session['admin_id'] = str(admin['_id'])
                session['admin_username'] = admin['username']
                flash("Admin logged in successfully.", "success")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid admin username or password.", "danger")
                
        except PyMongoError as err:
            flash(f"Database error: {err}", "danger")
            
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        db = get_db()
        
        # Calculate statistics counts
        total_users = db.users.count_documents({})
        total_searches = db.search_history.count_documents({})
        hospital_searches = db.search_history.count_documents({"emergency_type": "Hospital"})
        police_searches = db.search_history.count_documents({"emergency_type": "Police"})
        fire_searches = db.search_history.count_documents({"emergency_type": "Fire"})
        total_routes = db.route_history.count_documents({})
        
        stats = {
            "total_users": total_users,
            "total_searches": total_searches,
            "hospital_searches": hospital_searches,
            "police_searches": police_searches,
            "fire_searches": fire_searches,
            "total_routes": total_routes
        }
        
        return render_template('admin/dashboard.html', stats=stats)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('admin/dashboard.html', stats={})

@app.route('/admin/users')
@admin_required
def admin_users():
    try:
        db = get_db()
        users = list(db.users.find().sort("created_at", pymongo.DESCENDING))
        for user in users:
            user['id'] = str(user['_id'])
        return render_template('admin/users.html', users=users)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('admin/users.html', users=[])

@app.route('/admin/users/delete/<string:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    try:
        db = get_db()
        
        # Delete user document
        db.users.delete_one({"_id": ObjectId(user_id)})
        
        # Manual Cascade: Delete associated history logs matching user_id
        db.search_history.delete_many({"user_id": user_id})
        db.route_history.delete_many({"user_id": user_id})
        
        flash("User and associated history deleted successfully.", "success")
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
    return redirect(url_for('admin_users'))

@app.route('/admin/search-history')
@admin_required
def admin_search_history():
    search_type = request.args.get('type', '').strip()
    search_date = request.args.get('date', '').strip()
    
    query = {}
    if search_type:
        query["emergency_type"] = search_type
        
    if search_date:
        try:
            # Parse date string to match document's date range (start to end of selected day)
            date_parsed = datetime.strptime(search_date, "%Y-%m-%d")
            start_date = datetime(date_parsed.year, date_parsed.month, date_parsed.day, 0, 0, 0)
            end_date = datetime(date_parsed.year, date_parsed.month, date_parsed.day, 23, 59, 59)
            query["searched_at"] = {"$gte": start_date, "$lte": end_date}
        except ValueError:
            pass
            
    try:
        db = get_db()
        history = list(db.search_history.find(query).sort("searched_at", pymongo.DESCENDING))
        
        # Collect unique user ObjectIds for batch lookup
        user_ids = []
        for log in history:
            log['id'] = str(log['_id'])
            if log.get('user_id'):
                try:
                    user_ids.append(ObjectId(log['user_id']))
                except Exception:
                    pass
        
        # Batch fetch all referenced users in one query
        users_map = {}
        if user_ids:
            found_users = db.users.find({"_id": {"$in": user_ids}})
            for u in found_users:
                users_map[str(u['_id'])] = u

        # Map user details cleanly
        for log in history:
            user = users_map.get(str(log.get('user_id')))
            if user:
                log['name'] = user['name']
                log['email'] = user['email']
            else:
                log['name'] = 'Unknown User'
                log['email'] = 'N/A'
                
        return render_template('admin/search_history.html', history=history, selected_type=search_type, selected_date=search_date)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('admin/search_history.html', history=[], selected_type=search_type, selected_date=search_date)

@app.route('/admin/route-history')
@admin_required
def admin_route_history():
    try:
        db = get_db()
        routes = list(db.route_history.find().sort("created_at", pymongo.DESCENDING))
        
        # Collect unique user ObjectIds for batch lookup
        user_ids = []
        for r in routes:
            r['id'] = str(r['_id'])
            if r.get('user_id'):
                try:
                    user_ids.append(ObjectId(r['user_id']))
                except Exception:
                    pass

        # Batch fetch all referenced users in one query
        users_map = {}
        if user_ids:
            found_users = db.users.find({"_id": {"$in": user_ids}})
            for u in found_users:
                users_map[str(u['_id'])] = u

        # Map user details cleanly
        for r in routes:
            user = users_map.get(str(r.get('user_id')))
            if user:
                r['name'] = user['name']
                r['email'] = user['email']
            else:
                r['name'] = 'Unknown User'
                r['email'] = 'N/A'
                
        return render_template('admin/route_history.html', routes=routes)
    except PyMongoError as err:
        flash(f"Database error: {err}", "danger")
        return render_template('admin/route_history.html', routes=[])

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash("Admin logged out successfully.", "info")
    return redirect(url_for('admin_login'))


# ==================================================
# SERVER BOOT
# ==================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
