# CaiRO Travel API

A FastAPI server that exposes travel planning functions including itinerary creation, flight search, and hotel search.

## Features

- **Create Itinerary**: Generate optimized travel itineraries using AI
- **Search Flights**: Find flights using grounded search with Google Flights
- **Search Hotels**: Find hotels using grounded search with Google Hotels

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

3. Start the server:
```bash
python start_server.py
```

Or directly:
```bash
python main.py
```

The server will be available at `http://localhost:3001`

## API Documentation

- Swagger UI: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`

## Endpoints

### 1. Create Itinerary
**POST** `/api/itinerary/generate`

Create an optimized travel itinerary for a given city.

**Request Body:**
```json
{
  "source": "New Delhi",
  "destination": "Paris",
  "departureDate": "2025-06-15",
  "arrivalDate": "2025-06-20",
  "days": 5,
  "trip_theme": "Cultural and Historical",
  "user_mood": "Relaxed",
  "vibe_keywords": ["art", "museums", "cafes"],
  "activities": ["museums", "art galleries", "walking tours"],
  "avoid": ["crowded places", "long bus rides"],
  "been_here_before": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "day_1": [...],
    "day_2": [...],
    "day_3": [...]
  }
}
```

### 2. Search Flights
**POST** `/api/flights/generate`

Search for flight information using grounded search.

**Request Body:**
```json
{
  "source": "New Delhi",
  "destination": "Mumbai",
  "departureDate": "2025-06-27",
  "arrivalDate": "2025-06-30",
  "days": 3,
  "trip_theme": "Business",
  "user_mood": "Efficient",
  "vibe_keywords": ["quick", "comfortable"],
  "activities": ["business meetings"],
  "avoid": ["delays"],
  "been_here_before": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "indigo": {
      "06:25": "₹4500",
      "14:30": "₹4200"
    },
    "air_india": {
      "08:15": "₹5000"
    }
  }
}
```

### 3. Search Hotels
**POST** `/api/hotels/generate`

Search for hotel information using grounded search.

**Request Body:**
```json
{
  "source": "New Delhi",
  "destination": "Bangalore",
  "departureDate": "2025-06-24",
  "arrivalDate": "2025-06-29",
  "days": 5,
  "trip_theme": "Leisure",
  "user_mood": "Adventurous",
  "vibe_keywords": ["comfortable", "modern"],
  "activities": ["sightseeing", "local food"],
  "avoid": ["noisy areas"],
  "been_here_before": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "Hotel Sigma Suites",
    "price_per_night": "1283",
    "rating": "4.2",
    "location": "Gandhi Nagar, Bangalore"
  }
}
```

### 4. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "CaiRO Travel API is running"
}
```

### 5. Root Endpoint
**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to CaiRO Travel API",
  "endpoints": {
    "generate_itinerary": "/api/itinerary/generate",
    "generate_flights": "/api/flights/generate", 
    "generate_hotels": "/api/hotels/generate"
  }
}
```

## Example Usage with curl

### Create Itinerary
```bash
curl -X POST "http://localhost:3001/api/itinerary/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "Mumbai",
       "destination": "Tokyo",
       "departureDate": "2025-07-15",
       "arrivalDate": "2025-07-20",
       "days": 5,
       "trip_theme": "Cultural Exploration",
       "user_mood": "Curious",
       "vibe_keywords": ["technology", "anime", "traditional"],
       "activities": ["museums", "temples", "food tours"],
       "avoid": ["crowded trains during rush hour"],
       "been_here_before": false
     }'
```

### Search Flights
```bash
curl -X POST "http://localhost:3001/api/flights/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "Delhi",
       "destination": "Goa",
       "departureDate": "2025-07-15",
       "arrivalDate": "2025-07-18",
       "days": 3,
       "trip_theme": "Beach Vacation",
       "user_mood": "Relaxed",
       "vibe_keywords": ["beach", "sun", "relaxation"],
       "activities": ["beach activities", "water sports"],
       "avoid": ["early morning flights"],
       "been_here_before": false
     }'
```

### Search Hotels
```bash
curl -X POST "http://localhost:3001/api/hotels/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "Mumbai",
       "destination": "Goa",
       "departureDate": "2025-07-15",
       "arrivalDate": "2025-07-18",
       "days": 3,
       "trip_theme": "Beach Vacation",
       "user_mood": "Relaxed",
       "vibe_keywords": ["beachfront", "comfortable"],
       "activities": ["beach activities", "spa"],
       "avoid": ["noisy locations"],
       "been_here_before": false
     }'
```

## Request Body Schema

All endpoints use the unified `TripFormOutput` schema:

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Departure city/location |
| `destination` | string | Destination city/location |
| `departureDate` | string | Departure date (YYYY-MM-DD format) |
| `arrivalDate` | string | Return/checkout date (YYYY-MM-DD format) |
| `days` | integer | Number of days for the trip |
| `trip_theme` | string | Theme of the trip (e.g., "Cultural", "Adventure", "Business") |
| `user_mood` | string | User's mood/preference (e.g., "Relaxed", "Adventurous") |
| `vibe_keywords` | array of strings | Keywords describing desired vibe |
| `activities` | array of strings | Preferred activities |
| `avoid` | array of strings | Things to avoid |
| `been_here_before` | boolean | Whether user has visited the destination before |

## Environment Variables

- `GEMINI_API_KEY`: Your Gemini API key (required)

## Error Handling

All endpoints return proper HTTP status codes:
- `200`: Success
- `422`: Validation Error (invalid request body)
- `500`: Internal Server Error

Error responses include details:
```json
{
  "detail": "Error message describing what went wrong"
}
``` 