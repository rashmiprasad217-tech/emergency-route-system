# Emergency Route System (MongoDB Edition)

A complete, fully functional college-level final-year web application project built using Python Flask, MongoDB, and the Google Maps API. The application detects the user's location via standard browser GPS geolocation and maps the shortest driving path to nearby emergency services (Hospitals, Police Stations, and Fire Stations), including calculations for distance and duration.

---

## 1. Project Introduction
During emergencies, finding the closest healthcare center, precinct, or rescue station can be a life-or-death scenario. Standard mapping software often requires multiple searches, filtering, and manual location inputs. 
The **Emergency Route System** addresses this problem by offering a dedicated, easy-to-use dashboard that automates location lookup, fetches emergency services in a 5km radius via the Google Places API, and plots driving route details on an interactive map at the click of a button. It includes a user profile manager, audit logs for search and route history, and a secure administrator dashboard for data analysis and user management.

---

## 2. Project Objectives
1. **Reduce Emergency Response/Search Time:** Helping users find critical locations within seconds.
2. **Dynamic Location Awareness:** Integrating HTML5 Geolocation to automatically query the surrounding environment.
3. **Map Visualization:** Placing categorized marker pins for hospitals, police stations, and fire stations on a Google Map canvas.
4. **Calculated Navigation Paths:** Displaying standard driving lines, exact distance metrics, and time duration estimates.
5. **Auditable System Logs:** Retaining history logs for user search trends and navigation calculations.
6. **Administrative Insights:** Providing graphical and numeric stats to manage users and audit database health.

---

## 3. Technology Stack

### Front-End:
- **HTML5 & CSS3** (Vanilla styling, responsive adjustments)
- **Bootstrap 5** (Layout container grid, tables, inputs, modal dialogs)
- **Font Awesome 6 & Bootstrap Icons** (Aesthetic markers and category icons)
- **Vanilla JavaScript** (AJAX requests, DOM validation, and API integrations)

### Back-End:
- **Python** (Flask Framework)
- **Werkzeug** (Secure PBKDF2 SHA256 password hashing)
- **python-dotenv** (Local environment variable parser)

### Database:
- **MongoDB** (NoSQL document database)
- **pymongo** (Python connection driver)
- **dnspython** (For cloud Atlas connections)

### APIs:
- **Google Maps JavaScript API** (Interactive map canvas)
- **Google Places API** (Nearby facility queries)
- **Google Directions API** (Navigation routing and driving metrics)
- **HTML5 Geolocation API** (Client GPS coordinates)

---

## 4. Folder Structure
```text
emergency-route-system/
│
├── app.py                  # Main Flask application logic & API endpoints
├── config.py               # Flask and database environment configurations
├── requirements.txt        # Python package dependency definitions
├── .env.example            # Environment configuration template
├── .gitignore              # Excluded development cache & secrets files
├── README.md               # User guide and setup documentation
│
├── static/
│   ├── css/
│   │   └── style.css       # Design tokens, custom colors, animations
│   └── js/
│       ├── main.js         # Bootstrap UI helpers and alerts controller
│       └── maps.js         # Google Maps canvas, Geolocation, Places, and routing
│
├── templates/
│   ├── base.html           # Core HTML skeleton container
│   ├── navbar.html         # Dynamic role-based navigation bar
│   ├── index.html          # Public landing portal
│   ├── about.html          # Project summary and technology details
│   ├── contact.html        # Simulated contact page
│   ├── login.html          # User login
│   ├── register.html       # User signup
│   ├── dashboard.html      # Interactive emergency map interface
│   ├── search_history.html # User search audits
│   ├── route_history.html  # User route logs
│   ├── profile.html        # Profile management (password update)
│   ├── db_error.html       # Database connection failure error handler
│   │
│   └── admin/
│       ├── login.html      # Admin portal login
│       ├── dashboard.html  # Statistics cards
│       ├── users.html      # User tables (cascading delete triggers)
│       ├── search_history.html # Global user search audit tables with filters
│       └── route_history.html  # Global user route directions table
│
└── scripts/
    └── create_admin.py     # Secure admin registration script
```

---

## 5. Installation Instructions

### STEP 1: Install Python
Ensure Python 3.8 or higher is installed. Check using:
```bash
python --version
```

### STEP 2: Setup Database (MongoDB)
You can run MongoDB in two ways:
#### Option A: Cloud Database (MongoDB Atlas) - *Recommended, no installation required*
1. Sign up for a free account at [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas).
2. Create a Free Shared Cluster.
3. Add a Database User (keep note of the password).
4. Whitelist your current IP address in the Network Access tab.
5. Click **Connect > Drivers**, copy the connection URI, and paste it into your `.env` file as `MONGO_URI`.

#### Option B: Local Database (MongoDB Community Server)
1. Download and install [MongoDB Community Server](https://www.mongodb.com/try/download/community) for Windows.
2. Follow the setup wizard. Ensure **"Install MongoDB as a Service"** is checked.
3. Once installed, it runs locally on port `27017` with the default connection URI: `mongodb://localhost:27017/emergency_route_system`.

### STEP 3: Setup project folder
Place the `emergency-route-system` folder in your preferred workspace.

### STEP 4: Setup Python Virtual Environment
Open a terminal in the `emergency-route-system` directory:
```bash
# Create Virtual Environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### STEP 5: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### STEP 6: Configure Environment Variables
Copy `.env.example` and rename it to `.env`:
```bash
cp .env.example .env
```
Open `.env` and enter your database details and your Google Maps API Key:
```text
SECRET_KEY=YOUR_SUPER_SECRET_KEY_HERE
MONGO_URI=mongodb://localhost:27017/emergency_route_system
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE
```

---

## 6. Google Maps API Setup

For the map integration to function correctly, you must enable three services within your Google Cloud Console:
1. **Maps JavaScript API:** Renders the map canvas on the dashboard.
2. **Places API:** Performs radius keyword queries for hospitals, police stations, and fire stations.
3. **Directions API:** Plots driving lines and measures routes (distance/time).

### How to Create an API Key:
1. Log in to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Emergency-Route-System`).
3. Navigate to **APIs & Services > Library**, search for and **Enable** the 3 APIs listed above.
4. Go to **APIs & Services > Credentials** and click **+ Create Credentials > API Key**.
5. Copy the generated key and paste it as the value of `GOOGLE_MAPS_API_KEY` in your `.env` file.

---

## 7. Run the Application

### STEP 1: Create Admin Account
Before starting the server, run the administrative command line script to create the master administrator account. In the virtual environment terminal, run:
```bash
python scripts/create_admin.py
```
- It will prompt for a username (defaults to `admin`).
- Enter a password and confirm it. This password will be securely hashed in MongoDB.

### STEP 2: Start Flask Server
Start the development web server:
```bash
python app.py
```

### STEP 3: Open in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```
---

## 8. Troubleshooting
- **Database Connection Error page:** Ensure the MongoDB Community Server service is started (check `services.msc` on Windows) or verify that your Atlas cluster connection URI and login details in `.env` are correct.
- **Map fails to load / Grey Screen:** Verify that `GOOGLE_MAPS_API_KEY` is loaded correctly in `.env` and that you enabled all three APIs in the Google Cloud Console.
- **Location permissions blocked:** Geolocation requires user permission. Reset location access permissions next to your browser URL address bar and reload.
