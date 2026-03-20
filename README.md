# Ride Sharing API

A basic ride sharing REST API built with Django REST Framework with JWT authentication.

## Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Authentication
```
POST /register/    {"username": "john", "password": "pass123", "role": "rider/driver"}
POST /login/       {"username": "john", "password": "pass123"}
POST /logout/
```

### Rider
```
POST  /rides/                    {"pickup_location": "Thrissur", "dropoff_location": "Kochi"}
GET   /rides/                    list all rides
GET   /rides/<id>/               ride details
GET   /rides/match_driver/       find available drivers for current ride request
```

### Driver
```
PATCH /rides/<id>/accept_ride/              accept a ride request
PATCH /rides/<id>/update_status/            {"status": "started/completed/cancelled"}
PATCH /rides/<id>/update_current_location/  {"current_location": "Chalakudy"}
```

## Bonus Features

### Real-time Ride Tracking 
When a ride is started, the current location is set to the pickup location.
The driver can update the current location periodically using the `update_current_location` endpoint to simulate movement during the ride.
When the ride is completed, the location is set to the dropoff location.

### Ride Matching 
The `match_driver` endpoint tries to find available drivers for a ride request.
Drivers who recently completed a ride near the pickup location are prioritized.
If none are found, the system returns any available driver.