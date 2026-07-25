# Emergency Route System: College Project Documentation (MongoDB Edition)

---

## 1. Project Abstract
The **Emergency Route System** is a web-based, geolocation-aware routing portal designed to locate nearby emergency services (Hospitals, Police Stations, and Fire Stations) and map the shortest driving route to them. Built using Python Flask, MongoDB, and Google Maps Platform APIs, the system automatically detects a user's location via browser GPS and visualizes surrounding facilities on an interactive map. It implements secure authentication using session management and secure password hashing. Users can view their search and route history, while administrators can review global statistics, manage users, and filter audit logs. The system is designed to minimize response delays and streamline navigational routing during critical emergencies.

---

## 2. Introduction
During accidents, medical conditions, or security emergencies, response time is critical. Finding local aid centers quickly is paramount. While general-purpose navigation apps exist, they can be cluttered and slow to query. This project implements a dedicated portal optimized for emergency response. It loads a clean, focused user interface, requests GPS location permission, and allows users to search for critical services within a 5km radius. It automatically plots the shortest driving path with distance and time details.

---

## 3. Problem Statement
During critical emergencies, delays occur due to:
1. **Inefficient Search Workflows:** Users must manually type their current address or locate themselves on generic map services, causing delays.
2. **Cluttered Map Listings:** Search results on generic mapping apps include advertisements, reviews, and unrelated businesses, which can distract from identifying emergency hubs.
3. **Lack of Audits:** Users cannot easily keep logs of route coordinates, distance, and duration metrics.
4. **Poor Administration:** Municipal coordinators lack access to centralized statistics regarding user search history logs to track emergency request trends.

---

## 4. Proposed Solution
The proposed Emergency Route System addresses these issues:
1. **Single-Click Location Resolution:** Incorporates HTML5 Geolocation to acquire active GPS coordinates automatically.
2. **Targeted Service Categorization:** Provides dedicated buttons for Hospital, Police Station, and Fire Station searches to filter out irrelevant map markers.
3. **Dedicated Routing Logic:** Employs the Google Directions API to plot paths, driving distances, and travel durations.
4. **Persistent History Audits:** Automatically logs searches and generated routes to a MongoDB database.
5. **Centralized Admin Control Panel:** Enables administrators to monitor system usage, analyze search statistics, filter audit logs, and delete user accounts.

---

## 5. Objectives
1. Automatically capture current GPS coordinates of the user.
2. Search and filter nearby hospitals, police stations, and fire stations within 5km.
3. Render interactive pins and detailed info windows on a Google Maps canvas.
4. Plot the driving route from the user's location to the chosen facility.
5. Display driving distance and estimated travel duration.
6. Save and view search history logs and route history logs.
7. Provide secure user and admin authentication systems.
8. Provide administrator tools to monitor statistics and manage user records.

---

## 6. Scope of Project
The scope includes a fully functional web-based emergency portal accessible on desktops, tablets, and mobile devices. It provides location querying, map rendering, driving path overlays, and history logs. 
**Out of Scope (Future Work):** Live traffic delays, SOS notifications to family contacts, real-time ambulance tracking, and offline routing maps.

---

## 7. Technology Used
- **Backend Framework:** Python Flask
- **Database Engine:** MongoDB (NoSQL Document Store)
- **Database Driver:** pymongo & dnspython
- **Front-End Styling:** HTML5, CSS3, Bootstrap 5, Font Awesome 6 Icons
- **Scripting Language:** Vanilla JavaScript (ES6)
- **API Services:** Google Maps JavaScript API, Google Places API, Google Directions API, Browser Geolocation API
- **Security Utilities:** Werkzeug Password Hashing

---

## 8. Hardware Requirements
- **Processor:** Dual-core Intel Core i3 or equivalent AMD processor (minimum); Core i5/i7 (recommended).
- **RAM:** 4 GB (minimum); 8 GB or higher (recommended).
- **Hard Disk:** 500 MB of free storage space for code files and database logs.
- **Client Devices:** Any GPS-enabled smartphone, tablet, laptop, or desktop.

---

## 9. Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Development Environment:** Visual Studio Code or PyCharm.
- **Database Server:** MongoDB Community Server or MongoDB Atlas (Cloud).
- **Web Browser:** Google Chrome, Mozilla Firefox, Microsoft Edge, or Apple Safari (with GPS/Location services enabled).
- **Python Engine:** Python 3.8+ (with virtualenv installed).

---

## 10. Functional Requirements
1. **User Sign Up & Login:** Create an account and authenticate securely.
2. **Current Location Resolution:** Query browser Geolocation to determine latitude and longitude.
3. **Emergency Search Filters:** Click quick buttons to trigger Hospital, Police, or Fire Station lookups.
4. **Map Pins & Labels:** Display location markers with custom icons and info windows on click.
5. **Route Navigation:** Plot driving directions and estimate distance and travel time.
6. **Logs Retention:** Store searches and route maps to search_history and route_history database collections.
7. **Admin Dashboard:** Display system stats (total users, category searches, routes).
8. **Admin User Control:** View and delete user profiles, with cascading deletion of user logs.
9. **Admin Log Filter:** View all user searches, with filters for category type and search date.

---

## 11. Non-Functional Requirements
1. **Response Time:** Geolocation and Place search results should render in under 3 seconds (network dependent).
2. **Security:** Implement session authentication checks, Werkzeug password hashing, and parameterized MongoDB queries to prevent injection attacks.
3. **Usability:** Designed with clean Bootstrap cards and responsive grids for easy mobile navigation.
4. **Reliability:** Graceful error handling for missing database connections, blocked GPS permissions, or API failures.
5. **Maintainability:** Modular structure (config.py, app.py, and separate static/templates folders) with clear code comments.

---

## 12. System Architecture
The system follows a standard Three-Tier Client-Server Architecture:
1. **Presentation Layer (Front-End):** Bootstrap 5, HTML, CSS, and JavaScript. Runs in the client browser, coordinates geolocation coordinates, and interfaces with the Google Maps Web API.
2. **Application Layer (Back-End Server):** Python Flask application (`app.py`). Handles route requests, manages sessions, secures auth, processes APIs, and runs database queries.
3. **Data Layer (Database):** MongoDB Server database storing persistent logs in the `users`, `admins`, `search_history`, and `route_history` collections.

---

## 13. Database Schema Explanation (MongoDB NoSQL Collections)
Unlike relational databases, MongoDB stores records as JSON-like documents. The database contains 4 main collections:
1. `users`: Stores user profile details.
   - Document structure: `{_id: ObjectId, name, email, phone, password, created_at: Date}`
2. `admins`: Stores admin portal accounts.
   - Document structure: `{_id: ObjectId, username, password, created_at: Date}`
3. `search_history`: Tracks search queries.
   - Document structure: `{_id: ObjectId, user_id: string (matching users._id), emergency_type, latitude: float, longitude: float, searched_at: Date}`
4. `route_history`: Tracks directions.
   - Document structure: `{_id: ObjectId, user_id: string (matching users._id), service_name, service_type, destination_address, destination_latitude: float, destination_longitude: float, distance, estimated_time, created_at: Date}`

Cascading deletion behavior is implemented programmatically in Python: when a user account is deleted by an admin, the system automatically runs `delete_many` queries to clean up all logs containing that user's `user_id`.

---

## 14. Entity-Relationship (ER) Diagram Description (NoSQL Conceptual Model)
- **Entity USER:** Attributes: `_id` (ID Key), `name`, `email`, `phone`, `password`, `created_at`.
- **Entity ADMIN:** Attributes: `_id` (ID Key), `username`, `password`, `created_at`.
- **Entity SEARCH_HISTORY:** Attributes: `_id` (ID Key), `user_id` (Link), `emergency_type`, `latitude`, `longitude`, `searched_at`.
- **Entity ROUTE_HISTORY:** Attributes: `_id` (ID Key), `user_id` (Link), `service_name`, `service_type`, `destination_address`, `destination_latitude`, `destination_longitude`, `distance`, `estimated_time`, `created_at`.

### Relationships:
- **USER to SEARCH_HISTORY (1 to Many):** One user can make multiple emergency searches. When a user is deleted, their associated search history is also deleted.
- **USER to ROUTE_HISTORY (1 to Many):** One user can request directions to multiple facilities. Deleting a user deletes their route history.
- **ADMIN** acts as an independent entity managing the overall system.

---

## 15. Data Flow Diagram (DFD) Description

### Level 0 DFD (Context Diagram):
- **User Entity:** Sends registration/login credentials, location permission, and search requests to the system. Receives map visuals, facility lists, and driving directions.
- **Admin Entity:** Sends admin credentials and deletion requests. Receives dashboard statistics, user tables, search logs, and routing metrics.
- **Google Maps API:** Receives search requests. Returns map tiles, coordinate markers, and path coordinates.

### Level 1 DFD (Sub-Processes):
1. **User Authentication:** Interfaces with the `users` collection to authenticate logins and signups.
2. **Location Resolution:** Captures client GPS coordinates via browser Geolocation.
3. **Emergency Search:** Queries the Google Places API with client coordinates. Writes search records to the `search_history` collection.
4. **Path Calculations:** Queries the Google Directions API for driving paths. Writes route records to the `route_history` collection.
5. **System Management:** Extracts database metrics for the admin dashboard. Performs user deletion queries on the `users` collection.

---

## 16. Use Case Diagram Description
- **Actors:** User, Admin, Google Maps API.
- **User Use Cases:** Register Account, Log In, Share GPS Location, Search Emergency Service, View Map Markers, Get Driving Directions, View Search History, View Route History, Manage Profile.
- **Admin Use Cases:** Log In Admin, View Dashboard Statistics, Manage Users (View/Delete), Audit Search History, Audit Route History.
- **Google Maps API Actor:** Serves Map Tiles, Resolves Places, Provides Route Paths.

---

## 17. Module Description
1. **Authentication Module:** Handles secure signup, login, and logout for users and administrators.
2. **Dashboard Map Module:** Coordinates HTML5 Geolocation and initializes the Google Maps canvas with user position markers.
3. **Places Query Module:** Filters search queries (Hospital, Police, Fire) within a 5km radius using the Google Places API.
4. **Directions Routing Module:** Queries the Google Directions API to plot route lines, and calculates driving distance and duration.
5. **Database Logger Module:** Saves search history logs and calculated route metrics to MongoDB collections.
6. **Administration Module:** Summarizes statistics for the admin panel and manages user account deletions.

---

## 18. Testing
- **Unit Testing:** Validated database connection routines, helper password hashing functions, and API response parsing.
- **Functional Testing:** Verified that the signup form enforces email formats, matches passwords, prevents duplicate emails, and creates secure hashes. Verified that geolocation is captured successfully when permission is granted.
- **Security Testing:** Proved session restrictions block unauthenticated access to the user dashboard and profile pages.
- **User Acceptance Testing (UAT):** Tested end-to-end user and admin workflows to ensure the system is responsive on desktops, tablets, and mobile devices.

---

## 19. Advantages
1. **No SQL Schemas:** Flexible document models allow dynamic data changes.
2. **Dedicated Interface:** A simple, ad-free interface optimized for emergencies.
3. **Automated Geolocation:** No manual address entry required.
4. **Driving Path Overlays:** Visual routes on the map alongside step-by-step instructions.
5. **Secure Administration:** Dedicated login credentials with secure password storage.

---

## 20. Limitations
1. **Requires Internet Connection:** The application relies on external Google Maps Cloud APIs.
2. **Requires GPS/Location Services:** Users must grant location access permissions for full functionality.
3. **API Usage Limits:** Google APIs require billing configurations and have daily usage quotas.
4. **Driving Mode Default:** Does not account for walking or helicopter transit paths.

---

## 21. Future Enhancements
- **Live Traffic Updates:** Color-coded traffic indicators along route lines.
- **SMS SOS Broadcast:** Automatic emergency SMS alerts sent to family contacts.
- **Offline Routing Maps:** Basic local navigation overlays when internet connection is lost.
- **SOS Alarm Button:** A panic button that sounds a siren on the mobile device.

---

## 22. Conclusion
The **Emergency Route System** is an effective, dedicated tool for locating emergency services. By combining Python Flask, MongoDB, and the Google Maps API, it provides a functional platform for search and routing during emergencies. It serves as a comprehensive BCA/MCA final-year college project demonstrating full-stack development, database management, and API integration.

---

## 23. Viva Questions & Answers (MongoDB / NoSQL Edition)

#### Q1: What is the main objective of the Emergency Route System?
**A:** The main objective is to help users quickly find nearby emergency services (Hospitals, Police Stations, Fire Stations) based on their current location and get driving routes, reducing response times.

#### Q2: What technology stack is used in this project?
**A:** Flask (Python) for the backend, MongoDB for the database, HTML5/CSS3/Bootstrap 5 for the front-end, JavaScript for geolocation, and the Google Maps APIs for mapping and routing.

#### Q3: Why did you choose MongoDB instead of MySQL for this project?
**A:** MongoDB is a NoSQL document database. It is schema-less, highly scalable, and extremely easy to set up. It allows using a free cloud cluster (MongoDB Atlas), eliminating local database configuration errors common with MySQL (like user permission issues).

#### Q4: Which database driver connects Python to MongoDB?
**A:** We use `pymongo`. It is the official Python driver for MongoDB and supports connection pools, indexing, and direct JSON-like document querying.

#### Q5: How does the application detect the user's location?
**A:** It uses the standard HTML5 Browser Geolocation API (`navigator.geolocation.getCurrentPosition`) to capture the user's GPS latitude and longitude.

#### Q6: How does the application query nearby emergency services?
**A:** It uses the Google Maps Places Service (`google.maps.places.PlacesService`) nearby search to query locations with a 5000-meter radius, using keywords like 'hospital', 'police station', or 'fire station'.

#### Q7: Which Google Maps APIs need to be enabled for this project?
**A:** 1) Maps JavaScript API (for rendering maps), 2) Places API (for nearby searches), and 3) Directions API (for route generation).

#### Q8: Why is the Google Maps API Key and database URI stored in a `.env` file?
**A:** To keep them secure. Hardcoding keys can lead to security risks. Storing them in a `.env` file excluded by `.gitignore` ensures they remain private.

#### Q9: How does the backend pass configuration variables safely to the template?
**A:** Flask reads the variables using `python-dotenv` and the `Config` class, then passes them to the template via `render_template` (e.g., `maps_key=maps_key`), avoiding hardcoding in client files.

#### Q10: How are user passwords secured in the database?
**A:** Passwords are encrypted using Werkzeug's `generate_password_hash` helper, which uses secure PBKDF2 hashing. Plain-text passwords are never stored.

#### Q11: What is the purpose of the `create_admin.py` script?
**A:** It is a setup script that connects to MongoDB, prompts for admin credentials, hashes the password, and inserts the document into the `admins` collection.

#### Q12: What is a NoSQL database, and how does it store data?
**A:** A NoSQL database is a non-relational database. MongoDB stores data as documents in binary JSON format (BSON) grouped inside collections, rather than rows in tables.

#### Q13: How is cascading deletion handled in MongoDB since it lacks SQL foreign key constraints?
**A:** It is handled programmatically in the Flask backend code. When an administrator deletes a user, the route deletes the user document, and then runs `delete_many` queries to clean up all logs matching that user's `user_id` from the search and route collections.

#### Q14: How does the user dashboard transition from search results to route details?
**A:** It uses JavaScript. When a user clicks "Get Directions", JavaScript calls `directionsService.route`. On success, it hides the search results panel (`.classList.add('d-none')`) and displays the route info card.

#### Q15: How does the application handle database connection errors?
**A:** It registers a Flask error handler for `pymongo.errors.PyMongoError` that catches connection timeouts or failures, rendering a custom error page (`db_error.html`) detailing the issue and providing troubleshooting steps.

#### Q16: What is session management, and how is it used here?
**A:** Sessions allow the server to store user data across requests. We use Flask's signed cookie sessions to store the user's unique MongoDB string ID (`user_id`) to verify active logins.

#### Q17: What are Python decorators, and how are they used in this project?
**A:** Decorators modify the behavior of functions. We created `@login_required` and `@admin_required` decorators to restrict access to dashboard routes unless a valid session exists.

#### Q18: What is the purpose of the AJAX/API routes (`/api/save-search` and `/api/save-route`)?
**A:** They allow JavaScript to send search and route details to the Flask backend asynchronously (without reloading the page) to be logged in the database.

#### Q19: How are duplicate registrations prevented in MongoDB?
**A:** Before inserting a new user document, `app.py` queries the `users` collection using `db.users.find_one({"email": email})`. If a user is found, the system rejects the registration and flashes an error.

#### Q20: What happens if a user denies location access permissions?
**A:** The Geolocation API error callback is triggered. The system displays an alert (e.g. "Please allow location access to find nearby services") and falls back to default coordinates.

#### Q21: What is the default travel mode used for routing?
**A:** The default travel mode is `google.maps.TravelMode.DRIVING`, which calculates the best route for cars/vehicles.

#### Q22: How does the admin panel generate statistics in MongoDB?
**A:** When `admin/dashboard` is loaded, Flask executes `count_documents` queries (e.g. `db.users.count_documents({})`) on the database collections and passes the results to the dashboard template.

#### Q23: How can the admin filter search logs?
**A:** The admin search history page sends category type or date inputs via GET requests. Flask parses the date inputs and constructs a query dictionary (using operators like `$gte` and `$lte`) passed to the `find()` query.

#### Q24: What is the function of the `g` object in Flask?
**A:** The `g` object is a global namespace for storing data during a request. We use it to open a MongoDB client connection once and share it across functions, then close it at the end of the request.

#### Q25: Why is `@app.teardown_appcontext` used?
**A:** It registers a function to run when the request context is torn down, ensuring the MongoClient connection is closed properly to prevent resource leaks.

#### Q26: What are the main collections in the MongoDB database?
**A:** `users` (user profiles), `admins` (admin credentials), `search_history` (search parameters), and `route_history` (calculated route logs).

#### Q27: How is the application made responsive for mobile devices?
**A:** By using Bootstrap 5's responsive grid system (classes like `row`, `col-md-8`, `col-lg-4`), collapsible navigation menus, and fluid custom CSS.

#### Q28: How does the system display step-by-step directions?
**A:** The Directions API return object includes step instructions. Our script extracts this data, formats it into a list, and renders it inside a Bootstrap modal.

#### Q29: What are some security best practices implemented in this project?
**A:** Environment variables for secrets, secure password hashing, session-based access controls, and input validation.

#### Q30: What are some potential future enhancements for this system?
**A:** Real-time traffic integration, emergency SOS alerts via SMS, real-time ambulance tracking, and multi-language support.
