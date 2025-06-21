from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import json

# Import the functions from existing modules
from create_itnr import create_itinerary
from agents import search_flights, search_hotels

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create FastAPI app
app = FastAPI(
    title="CaiRO Travel API",
    description="API for creating itineraries and searching flights & hotels",
    version="1.0.0"
)

# Pydantic models for request bodies
class ItineraryRequest(BaseModel):
    city_name: str
    user_pref: str
    n_days: int
    model: str = "gemini-2.0-flash"

class FlightSearchRequest(BaseModel):
    source: str
    destination: str  
    date: str
    airlines: List[str]
    model: str = "gemini-2.5-pro"

class HotelSearchRequest(BaseModel):
    city: str
    check_in_date: str = None
    check_out_date: str = None
    price_min: int
    price_max: int
    model: str = "gemini-2.5-pro"

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to CaiRO Travel API",
        "endpoints": {
            "create_itinerary": "/itinerary",
            "search_flights": "/flights/search", 
            "search_hotels": "/hotels/search"
        }
    }

# Create itinerary endpoint
@app.post("/itinerary")
async def create_itinerary_endpoint(request: ItineraryRequest):
    """
    Create an optimized travel itinerary for a given city.
    
    Args:
        city_name: Name of the city for the trip
        user_pref: User preferences for the trip
        n_days: Number of days for the itinerary
        model: Gemini model to use (optional)
    
    Returns:
        JSON response with the created itinerary
    """
    try:
        logging.info(f"Creating itinerary for {request.city_name} ({request.n_days} days)")
        
        result = create_itinerary(
            city_name=request.city_name,
            user_pref=request.user_pref,
            n_days=request.n_days,
            model=request.model
        )
        
        # Try to parse the result as JSON to validate it
        try:
            parsed_result = json.loads(result)
            return {"status": "success", "data": parsed_result}
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"Error creating itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating itinerary: {str(e)}")

# Search flights endpoint
@app.post("/flights/search")
async def search_flights_endpoint(request: FlightSearchRequest):
    """
    Search for flight information using grounded search.
    
    Args:
        source: Source city
        destination: Destination city  
        date: Travel date
        airlines: List of airlines to search
        model: Gemini model to use (optional)
    
    Returns:
        JSON response with flight information
    """
    try:
        logging.info(f"Searching flights from {request.source} to {request.destination}")
        
        result = search_flights(
            source=request.source,
            destination=request.destination,
            date=request.date,
            airlines=request.airlines,
            model=request.model
        )
        
        # Try to parse the result as JSON
        try:
            parsed_result = json.loads(result)
            response = {"status": "success", "data": parsed_result}
            return response
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"Error searching flights: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

# Search hotels endpoint  
@app.post("/hotels/search")
async def search_hotels_endpoint(request: HotelSearchRequest):
    """
    Search for hotel information using grounded search.
    
    Args:
        city: City name
        check_in_date: Check-in date (optional)
        check_out_date: Check-out date (optional)
        price_min: Minimum price per night
        price_max: Maximum price per night
        model: Gemini model to use (optional)
    
    Returns:
        JSON response with hotel information
    """
    try:
        logging.info(f"Searching hotels in {request.city}")
        
        result = search_hotels(
            city=request.city,
            check_in_date=request.check_in_date,
            check_out_date=request.check_out_date,
            price_min=request.price_min,
            price_max=request.price_max,
            model=request.model
        )
        
        # Try to parse the result as JSON (now returns a single hotel)
        try:
            parsed_result = json.loads(result)
            response = {"status": "success", "data": parsed_result}
            return response
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"Error searching hotels: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching hotels: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "CaiRO Travel API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 