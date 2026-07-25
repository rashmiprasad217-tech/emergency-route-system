// Emergency Route System - Google Maps & Geolocation Integration

// Global variables
let map;
let userMarker;
let infoWindow;
let placesService;
let directionsService;
let directionsRenderer;
let markers = [];
let routeSteps = [];

// Fallback Coordinates (New Delhi, India)
let userLat = 28.6139;
let userLng = 77.2090;
let isLocationDetected = false;
let currentSearchType = '';
let navWatchId = null;
let isNavigating = false;

/**
 * Entry point callback for Google Maps API Script
 */
function initMap() {
    console.log("Google Maps API loaded successfully.");
    
    // Hide map loader overlay once initialized
    const mapLoader = document.getElementById('map-loader');
    if (mapLoader) {
        mapLoader.style.opacity = '0';
        setTimeout(() => mapLoader.style.display = 'none', 300);
    }

    // 1. Initialize Map Object
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: userLat, lng: userLng },
        zoom: 14,
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });

    // 2. Initialize Services
    infoWindow = new google.maps.InfoWindow();
    placesService = new google.maps.places.PlacesService(map);
    directionsService = new google.maps.DirectionsService();
    
    // Config Directions Renderer
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: false, // Keep default A/B markers for clarity
        polylineOptions: {
            strokeColor: "#198754", // Success Green
            strokeOpacity: 0.8,
            strokeWeight: 6
        }
    });

    // Enable Live Traffic Layer on Map View
    const trafficLayer = new google.maps.TrafficLayer();
    trafficLayer.setMap(map);

    // 3. Bind Geolocation Button Action
    const geoBtn = document.getElementById('btn-geolocation');
    if (geoBtn) {
        geoBtn.addEventListener('click', function() {
            detectUserLocation(true);
        });
    }

    // 4. Run immediate Geolocation detection on page load
    detectUserLocation(false);

    // 5. Check if search URL parameter is present (e.g. ?type=Hospital)
    const urlParams = new URLSearchParams(window.location.search);
    const typeParam = urlParams.get('type');
    if (typeParam) {
        // Wait briefly for geolocation coordinates before triggering Places search
        setTimeout(() => {
            triggerSearch(typeParam);
        }, 1200);
    }
}

/**
 * Attempts to detect user's current GPS coordinates using Browser Geolocation API
 * @param {boolean} showToast - Whether to show visual user alerts on success/failure
 */
function detectUserLocation(showToast = false) {
    const statusText = document.getElementById('location-status-text');
    const alertBox = document.getElementById('location-alert-box');

    if (!navigator.geolocation) {
        updateLocationStatus("Browser does not support geolocation.", "danger");
        if (showToast) showAlert("Your browser does not support GPS location detection.", "danger");
        return;
    }

    updateLocationStatus("Detecting location... Please check for GPS permission prompt.", "info");

    const geoOptions = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
        // Geolocation Success Callback
        function(position) {
            userLat = position.coords.latitude;
            userLng = position.coords.longitude;
            isLocationDetected = true;

            const userPos = { lat: userLat, lng: userLng };
            
            // Center map on user
            map.setCenter(userPos);
            map.setZoom(15);

            // Render User Position Marker
            if (userMarker) userMarker.setMap(null);

            userMarker = new google.maps.Marker({
                position: userPos,
                map: map,
                title: "Your Current Location",
                icon: {
                    url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png" // Blue dot for user
                }
            });

            // Bind click to show label
            userMarker.addListener('click', () => {
                infoWindow.setContent("<strong>Your Current Location</strong>");
                infoWindow.open(map, userMarker);
            });

            updateLocationStatus("GPS Coordinates loaded successfully.", "success");
            if (showToast) showAlert("GPS location detected successfully!", "success");

            // If user clicked location button while in a search, re-trigger active search type
            if (currentSearchType) {
                searchPlaces(currentSearchType);
            }
        },
        // Geolocation Error Callback
        function(error) {
            let errorMsg = "Unable to detect your location.";
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = "Please allow location access to find nearby emergency services.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = "Location information is unavailable.";
                    break;
                case error.TIMEOUT:
                    errorMsg = "The request to get user location timed out.";
                    break;
            }
            updateLocationStatus(errorMsg, "warning");
            if (showToast) showAlert(errorMsg, "warning");
        },
        geoOptions
    );
}

/**
 * Updates UI Alert bar based on Geolocation response
 */
function updateLocationStatus(message, type) {
    const statusText = document.getElementById('location-status-text');
    const alertBox = document.getElementById('location-alert-box');
    if (!statusText || !alertBox) return;

    statusText.textContent = message;
    alertBox.className = `alert alert-${type} border-0 shadow-sm d-flex align-items-center mb-4 p-3`;
}

/**
 * Main Trigger function called when Emergency Cards are clicked
 */
function triggerSearch(type) {
    currentSearchType = type;
    
    // Adjust active highlights on dashboard cards
    document.getElementById('card-hospital').classList.remove('active-service-card');
    document.getElementById('card-police').classList.remove('active-service-card');
    document.getElementById('card-fire').classList.remove('active-service-card');

    const activeCard = document.getElementById(`card-${type.toLowerCase()}`);
    if (activeCard) activeCard.classList.add('active-service-card');

    if (!isLocationDetected) {
        showAlert("Waiting for your GPS location. Attempting lookup...", "warning");
        detectUserLocation(true);
        return;
    }

    searchPlaces(type);
    saveSearchToHistory(type);
}

/**
 * Searches nearby locations using Google Places API Service
 */
function searchPlaces(type) {
    clearMapMarkers();
    clearActiveRoute();

    const userPos = { lat: userLat, lng: userLng };
    let request = {
        location: userPos,
        radius: 5000, // 5 km search radius
    };

    // Set keyword search query and Google Places type
    if (type === 'Hospital') {
        request.keyword = 'hospital';
        request.type = ['hospital'];
    } else if (type === 'Police') {
        request.keyword = 'police station';
        request.type = ['police'];
    } else if (type === 'Fire') {
        request.keyword = 'fire station';
        request.type = ['fire_station'];
    }

    const placeholder = document.getElementById('placeholder-text');
    const listContainer = document.getElementById('services-list-container');
    if (placeholder) placeholder.style.display = 'none';

    listContainer.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-danger mb-2" role="status"></div>
            <p class="text-muted small mb-0">Searching for nearby ${type}s...</p>
        </div>
    `;

    placesService.nearbySearch(request, function(results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
            renderPlacesList(results, type);
            renderPlacesMarkers(results, type);
        } else {
            listContainer.innerHTML = `
                <div class="alert alert-warning border-0 rounded-3 p-3 text-center my-3">
                    <i class="fa-solid fa-circle-exclamation fs-3 mb-2 text-warning"></i>
                    <p class="mb-0 fw-bold">No nearby services found</p>
                    <p class="text-muted small mb-0">Could not find any nearby ${type}s in a 5km radius.</p>
                </div>
            `;
            document.getElementById('active-marker-count').textContent = '0 Markers';
            showAlert(`No nearby ${type} services were found within 5km.`, "warning");
        }
    });
}

/**
 * Appends location marker pins to Google Map
 */
function renderPlacesMarkers(places, type) {
    let pinUrl = "https://maps.google.com/mapfiles/ms/icons/red-dot.png"; // Default red
    if (type === 'Police') pinUrl = "https://maps.google.com/mapfiles/ms/icons/blue-dot.png";
    if (type === 'Fire') pinUrl = "https://maps.google.com/mapfiles/ms/icons/orange-dot.png";

    places.forEach((place, index) => {
        const marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name,
            icon: { url: pinUrl }
        });

        // Store place data in marker
        marker.placeData = place;
        markers.push(marker);

        // Click marker action - trigger InfoWindow content
        marker.addListener('click', () => {
            const ratingHtml = place.rating ? `<span class="badge bg-warning text-dark ms-1"><i class="fa-solid fa-star me-1"></i>${place.rating}</span>` : '';
            const statusHtml = place.opening_hours ? `<div class="mt-1 small fw-bold ${place.opening_hours.open_now ? 'text-success' : 'text-danger'}">${place.opening_hours.open_now ? '● Open Now' : '● Closed'}</div>` : '';
            
            // Format Get directions args cleanly for escaping quotes
            const addressEscaped = place.vicinity.replace(/'/g, "\\'");
            const nameEscaped = place.name.replace(/'/g, "\\'");

            const infoHtml = `
                <div style="max-width: 200px;">
                    <h6 class="fw-bold mb-1">${place.name} ${ratingHtml}</h6>
                    <small class="text-muted d-block mb-1">${place.vicinity}</small>
                    ${statusHtml}
                    <button class="btn btn-success btn-sm w-100 mt-2 py-1 rounded" 
                            onclick="getDirections(${place.geometry.location.lat()}, ${place.geometry.location.lng()}, '${nameEscaped}', '${type}', '${addressEscaped}')">
                        <i class="fa-solid fa-route me-1"></i> Get Directions
                    </button>
                </div>
            `;
            infoWindow.setContent(infoHtml);
            infoWindow.open(map, marker);
        });
    });

    document.getElementById('active-marker-count').textContent = `${places.length} Markers`;
}

/**
 * Builds HTML components list displaying Place cards beside the map
 */
function renderPlacesList(places, type) {
    const listContainer = document.getElementById('services-list-container');
    listContainer.innerHTML = '';

    const listTitle = document.createElement('h5');
    listTitle.className = 'fw-bold text-dark mb-3 small text-uppercase';
    listTitle.textContent = `Nearby ${type}s`;
    listContainer.appendChild(listTitle);

    places.forEach((place, index) => {
        const ratingHtml = place.rating ? `<span class="badge bg-warning text-dark ms-2"><i class="fa-solid fa-star me-0.5"></i>${place.rating}</span>` : '';
        const statusHtml = place.opening_hours ? `<span class="ms-2 small fw-semibold ${place.opening_hours.open_now ? 'text-success' : 'text-danger'}">${place.opening_hours.open_now ? 'Open' : 'Closed'}</span>` : '';
        
        const addressEscaped = place.vicinity.replace(/'/g, "\\'");
        const nameEscaped = place.name.replace(/'/g, "\\'");

        const card = document.createElement('div');
        card.className = 'card border p-3 mb-3 bg-light bg-opacity-50';
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="fw-bold mb-0 text-dark" style="font-size: 0.95rem;">${index + 1}. ${place.name}</h6>
            </div>
            <p class="text-muted small mb-2"><i class="fa-solid fa-location-dot me-1"></i>${place.vicinity}</p>
            <div class="mb-3">
                <span class="badge bg-secondary bg-opacity-10 text-secondary border px-2 py-0.5 small">${type}</span>
                ${ratingHtml}
                ${statusHtml}
            </div>
            <div class="row g-2">
                <div class="col-6">
                    <button class="btn btn-outline-dark btn-sm w-100 py-1.5 rounded-2" onclick="focusPlace(${index})">
                        <i class="fa-solid fa-magnifying-glass-location me-1"></i> View Map
                    </button>
                </div>
                <div class="col-6">
                    <button class="btn btn-success btn-sm w-100 py-1.5 rounded-2" 
                            onclick="getDirections(${place.geometry.location.lat()}, ${place.geometry.location.lng()}, '${nameEscaped}', '${type}', '${addressEscaped}')">
                        <i class="fa-solid fa-route me-1"></i> Directions
                    </button>
                </div>
            </div>
        `;
        listContainer.appendChild(card);
    });
}

/**
 * Centers viewport on selected Place card marker
 */
function focusPlace(index) {
    if (markers[index]) {
        const marker = markers[index];
        map.panTo(marker.getPosition());
        map.setZoom(16);
        google.maps.event.trigger(marker, 'click');
    }
}

/**
 * Calculates transit driving directions using Directions Service
 */
function getDirections(destLat, destLng, destName, destType, destAddress) {
    const originPos = { lat: userLat, lng: userLng };
    const destPos = { lat: destLat, lng: destLng };

    const request = {
        origin: originPos,
        destination: destPos,
        travelMode: google.maps.TravelMode.DRIVING,
        drivingOptions: {
            departureTime: new Date(),
            trafficModel: google.maps.TrafficModel.BEST_GUESS
        },
        provideRouteAlternatives: true
    };

    directionsService.route(request, function(result, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            // Render path on map
            directionsRenderer.setDirections(result);

            // Get route summary info (uses duration_in_traffic when available for live traffic jams)
            const route = result.routes[0];
            const leg = route.legs[0];
            const distanceText = leg.distance.text;
            const durationText = leg.duration_in_traffic ? leg.duration_in_traffic.text : leg.duration.text;

            // Render route information card
            document.getElementById('results-card').classList.add('d-none');
            document.getElementById('route-info-card').classList.remove('d-none');

            document.getElementById('route-dest-name').textContent = destName;
            document.getElementById('route-distance').textContent = distanceText;
            document.getElementById('route-duration').textContent = durationText;

            // Extract instructions step list
            routeSteps = leg.steps.map(step => step.instructions);

            // Save calculated route logs into database history
            saveRouteToHistory(destName, destType, destAddress, destLat, destLng, distanceText, durationText);
            showAlert(`Route calculated: ${distanceText} driving route plotted.`, "success");
        } else {
            showAlert("Unable to calculate route. Route calculations failed.", "danger");
        }
    });
}

/**
 * Shows route list instructions in modal popup
 */
function showStepByStep() {
    const container = document.getElementById('directions-steps-container');
    if (!container) return;

    if (routeSteps.length === 0) {
        container.innerHTML = '<p class="text-muted">No direction steps available.</p>';
        return;
    }

    let stepsHtml = '<ol class="list-group list-group-numbered">';
    routeSteps.forEach((step, index) => {
        stepsHtml += `<li class="list-group-item border-0 py-2 small">${step}</li>`;
    });
    stepsHtml += '</ol>';

    container.innerHTML = stepsHtml;

    // Trigger bootstrap modal
    const directionsModal = new bootstrap.Modal(document.getElementById('directionsModal'));
    directionsModal.show();
}

/**
 * Clears active route path overlay and restores Places List
 */
function clearActiveRoute() {
    if (directionsRenderer) {
        directionsRenderer.setDirections({ routes: [] });
    }
    const routeInfoCard = document.getElementById('route-info-card');
    const resultsCard = document.getElementById('results-card');
    if (routeInfoCard) routeInfoCard.classList.add('d-none');
    if (resultsCard) resultsCard.classList.remove('d-none');
    routeSteps = [];
}

/**
 * Helper to remove all Place markers from map viewport
 */
function clearMapMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

// ==================================================
// AJAX / DATABASE LOGGER CALLS
// ==================================================

/**
 * Logs category searches to database via API
 */
function saveSearchToHistory(type) {
    fetch('/api/save-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emergency_type: type,
            latitude: userLat,
            longitude: userLng
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("Search history saved successfully.");
        } else {
            console.warn("Failed to log search history:", data.message);
        }
    })
    .catch(error => {
        console.error("AJAX Error logging search history:", error);
    });
}

/**
 * Logs route request queries to database via API
 */
function saveRouteToHistory(destName, destType, destAddress, destLat, destLng, distanceText, durationText) {
    fetch('/api/save-route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            service_name: destName,
            service_type: destType,
            destination_address: destAddress,
            destination_latitude: destLat,
            destination_longitude: destLng,
            distance: distanceText,
            estimated_time: durationText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("Route history logged successfully.");
        } else {
            console.warn("Failed to log route history:", data.message);
        }
    })
    .catch(error => {
        console.error("AJAX Error logging route history:", error);
    });
}

/**
 * Starts Real-Time Live GPS Navigation mode
 */
function startRealTimeNavigation() {
    if (!navigator.geolocation) {
        showAlert("Geolocation not supported for live tracking.", "danger");
        return;
    }

    isNavigating = true;

    // Toggle HUD & buttons
    const hud = document.getElementById('live-nav-hud');
    const btnStart = document.getElementById('btn-start-navigation');
    const btnStop = document.getElementById('btn-stop-navigation');

    if (hud) hud.classList.remove('d-none');
    if (btnStart) btnStart.classList.add('d-none');
    if (btnStop) btnStop.classList.remove('d-none');

    // Display first instruction if available
    const instrEl = document.getElementById('nav-current-instruction');
    if (instrEl && routeSteps.length > 0) {
        instrEl.innerHTML = routeSteps[0];
    }

    showAlert("Live GPS Navigation started! Tracking your movement...", "success");

    // Watch position in real time
    navWatchId = navigator.geolocation.watchPosition(
        function(position) {
            userLat = position.coords.latitude;
            userLng = position.coords.longitude;
            const newPos = { lat: userLat, lng: userLng };

            // Update user marker position smoothly
            if (userMarker) {
                userMarker.setPosition(newPos);
            }
            map.panTo(newPos);

            // Calculate live speed if available
            const speed = position.coords.speed; // speed in m/s
            const speedEl = document.getElementById('nav-speed-text');
            if (speedEl) {
                if (speed !== null && speed !== undefined && speed > 0) {
                    const kmh = (speed * 3.6).toFixed(0);
                    speedEl.innerHTML = `<i class="fa-solid fa-gauge-high me-1"></i>${kmh} km/h`;
                } else {
                    speedEl.innerHTML = `<i class="fa-solid fa-satellite-dish me-1"></i>GPS Active`;
                }
            }
        },
        function(error) {
            console.warn("Live Navigation GPS error:", error.message);
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
}

/**
 * Stops Real-Time Live GPS Navigation mode
 */
function stopRealTimeNavigation() {
    if (navWatchId !== null) {
        navigator.geolocation.clearWatch(navWatchId);
        navWatchId = null;
    }
    isNavigating = false;

    const hud = document.getElementById('live-nav-hud');
    const btnStart = document.getElementById('btn-start-navigation');
    const btnStop = document.getElementById('btn-stop-navigation');

    if (hud) hud.classList.add('d-none');
    if (btnStart) btnStart.classList.remove('d-none');
    if (btnStop) btnStop.classList.add('d-none');

    showAlert("Live GPS Navigation stopped.", "info");
}
