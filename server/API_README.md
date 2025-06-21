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

The server will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### 1. Create Itinerary
**POST** `/itinerary`

Create an optimized travel itinerary for a given city.

**Request Body:**
```json
{
  "city_name": "Paris",
  "user_pref": "I love museums, art galleries, and good food. I prefer walking over long bus rides.",
  "n_days": 3,
  "model": "gemini-2.0-flash"
}
```

**Response:**
```json
{
  "status": "success",
  "itinerary": {
    "day_1": [...],
    "day_2": [...],
    "day_3": [...]
  }
}
```

### 2. Search Flights
**POST** `/flights/search`

Search for flight information using grounded search.

**Request Body:**
```json
{
  "source": "bangalore",
  "destination": "mumbai",
  "date": "27 June 2025",
  "airlines": ["indigo", "air india", "vistara"],
  "model": "gemini-2.5-pro"
}
```

**Response:**
```json
{
  "status": "success",
  "flights": {
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
**POST** `/hotels/search`

Search for hotel information using grounded search.

**Request Body:**
```json
{
  "city": "bangalore",
  "check_in_date": "24 Jun 2025",
  "check_out_date": "29 Jun 2025",
  "price_min": 1000,
  "price_max": 2000,
  "model": "gemini-2.5-pro"
}
```

**Response:**
```json
{
  "status": "success",
  "hotels": [
    {
      "name": "Hotel Sigma Suites",
      "price_per_night": "1283",
      "rating": "4.2",
      "location": "Gandhi Nagar, Bangalore"
    },
    {
      "name": "Magaji Residency",
      "price_per_night": "1046",
      "rating": "3.9",
      "location": "Jayanagar, Bangalore"
    }
  ]
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

## Example Usage with curl

### Create Itinerary
```bash
curl -X POST "http://localhost:8000/itinerary" \
     -H "Content-Type: application/json" \
     -d '{
       "city_name": "Tokyo",
       "user_pref": "I love technology, anime culture, and traditional Japanese food",
       "n_days": 5
     }'
```

### Search Flights
```bash
curl -X POST "http://localhost:8000/flights/search" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "delhi",
       "destination": "goa",
       "date": "15 July 2025",
       "airlines": ["indigo", "spicejet", "air india"]
     }'
```

### Search Hotels
```bash
curl -X POST "http://localhost:8000/hotels/search" \
     -H "Content-Type: application/json" \
     -d '{
       "city": "goa",
       "check_in_date": "15 Jul 2025",
       "check_out_date": "18 Jul 2025",
       "price_min": 2000,
       "price_max": 5000
     }'
```

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