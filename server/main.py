from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
import json

# Import the functions from existing modules
from create_itnr import create_itinerary
from agents import search_flights, search_hotels

# ANSI Color codes for colored logging
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Background colors for API endpoint identification
    API_BG = '\033[43m'         # Yellow background
    ITINERARY_API_BG = '\033[46m'  # Cyan background
    FLIGHTS_API_BG = '\033[44m'    # Blue background
    HOTELS_API_BG = '\033[42m'     # Green background
    
    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    
    # API endpoint-specific prefixes
    API_PREFIX = f'{API_BG}{BLACK}{BOLD} 🌐 API {RESET}'
    ITINERARY_API_PREFIX = f'{ITINERARY_API_BG}{BLACK}{BOLD} 🗺️  ITINERARY API {RESET}'
    FLIGHTS_API_PREFIX = f'{FLIGHTS_API_BG}{WHITE}{BOLD} ✈️  FLIGHTS API {RESET}'
    HOTELS_API_PREFIX = f'{HOTELS_API_BG}{BLACK}{BOLD} 🏨 HOTELS API  {RESET}'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create FastAPI app
app = FastAPI(
    title="CaiRO Travel API",
    description="API for creating itineraries and searching flights & hotels",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic model for unified trip request body from client
class TripFormOutput(BaseModel):
    source: str
    destination: str
    departureDate: str
    arrivalDate: str
    days: int
    trip_theme: str
    user_mood: str
    vibe_keywords: List[str]
    activities: List[str]
    avoid: List[str]
    been_here_before: bool

# Root endpoint
@app.get("/")
async def root():
    logging.info(f"{Colors.API_PREFIX} {Colors.CYAN}🏠 Root endpoint accessed{Colors.RESET}")
    return {
        "message": "Welcome to CaiRO Travel API",
        "endpoints": {
            "generate_itinerary": "/api/itinerary/generate",
            "generate_flights": "/api/flights/generate", 
            "generate_hotels": "/api/hotels/generate"
        }
    }

# Create itinerary endpoint
@app.post("/api/itinerary/generate")
async def create_itinerary_endpoint(request: TripFormOutput):
    """
    Create an optimized travel itinerary for a given city.
    
    Args:
        TripFormOutput: Unified trip form data from client
    
    Returns:
        JSON response with the created itinerary
    """
    try:
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🚀 Creating itinerary for {request.destination} ({request.days} days){Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.BLUE}📋 Request data - Theme: {request.trip_theme}, Mood: {request.user_mood}{Colors.RESET}")
        
        # Transform client data to match create_itinerary function
        user_preferences = f"Trip theme: {request.trip_theme}. User mood: {request.user_mood}. Preferred activities: {', '.join(request.activities)}. Avoid: {', '.join(request.avoid)}"
        
        result = create_itinerary(
            city_name=request.destination,
            user_pref=user_preferences,
            n_days=request.days,
            model="gemini-2.0-flash"
        )
        
        # Try to parse the result as JSON to validate it
        try:
            parsed_result = json.loads(result)
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}✅ Itinerary created successfully{Colors.RESET}")
            return {"status": "success", "data": parsed_result}
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ Result is not valid JSON, returning as text{Colors.RESET}")
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error creating itinerary: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error creating itinerary: {str(e)}")

# Generate flights endpoint
@app.post("/api/flights/generate")
async def generate_flights_endpoint(request: TripFormOutput):
    """
    Search for flight information using grounded search.
    
    Args:
        TripFormOutput: Unified trip form data from client
    
    Returns:
        JSON response with flight information
    """
    try:
        logging.info(f"{Colors.FLIGHTS_API_PREFIX} {Colors.CYAN}🚀 Searching flights from {request.source} to {request.destination}{Colors.RESET}")
        logging.info(f"{Colors.FLIGHTS_API_PREFIX} {Colors.BLUE}📅 Departure date: {request.departureDate}{Colors.RESET}")
        
        # Use departure date and assume some default airlines if none specified
        default_airlines = ["IndiGo", "Air India", "Air India Express"]
        
        result = search_flights(
            source=request.source,
            destination=request.destination,
            date=request.departureDate,
            airlines=default_airlines,
            model="gemini-2.5-pro"
        )
        
        # Try to parse the result as JSON
        try:
            parsed_result = json.loads(result)
            logging.info(f"{Colors.FLIGHTS_API_PREFIX} {Colors.GREEN}✅ Flight search completed successfully{Colors.RESET}")
            response = {"status": "success", "data": parsed_result}
            return response
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            logging.warning(f"{Colors.FLIGHTS_API_PREFIX} {Colors.YELLOW}⚠️ Result is not valid JSON, returning as text{Colors.RESET}")
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"{Colors.FLIGHTS_API_PREFIX} {Colors.RED}❌ Error searching flights: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

# Generate hotels endpoint  
@app.post("/api/hotels/generate")
async def generate_hotels_endpoint(request: TripFormOutput):
    """
    Search for hotel information using grounded search.
    
    Args:
        TripFormOutput: Unified trip form data from client
    
    Returns:
        JSON response with hotel information
    """
    try:
        logging.info(f"{Colors.HOTELS_API_PREFIX} {Colors.CYAN}🚀 Searching hotels in {request.destination}{Colors.RESET}")
        logging.info(f"{Colors.HOTELS_API_PREFIX} {Colors.BLUE}📅 Check-in: {request.departureDate}, Check-out: {request.arrivalDate}{Colors.RESET}")
        
        # Set reasonable default price range if not specified
        price_min = 1000  # Default minimum price per night
        price_max = 2500 # Default maximum price per night
        
        result = search_hotels(
            city=request.destination,
            check_in_date=request.departureDate,
            check_out_date=request.arrivalDate,
            price_min=price_min,
            price_max=price_max,
            model="gemini-2.5-pro"
        )
        
        # Try to parse the result as JSON (now returns a single hotel)
        try:
            parsed_result = json.loads(result)
            logging.info(f"{Colors.HOTELS_API_PREFIX} {Colors.GREEN}✅ Hotel search completed successfully{Colors.RESET}")
            response = {"status": "success", "data": parsed_result}
            return response
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            logging.warning(f"{Colors.HOTELS_API_PREFIX} {Colors.YELLOW}⚠️ Result is not valid JSON, returning as text{Colors.RESET}")
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"{Colors.HOTELS_API_PREFIX} {Colors.RED}❌ Error searching hotels: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error searching hotels: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    logging.info(f"{Colors.API_PREFIX} {Colors.GREEN}💚 Health check accessed{Colors.RESET}")
    return {"status": "healthy", "message": "CaiRO Travel API is running"}

if __name__ == "__main__":
    import uvicorn
    logging.info(f"{Colors.API_PREFIX} {Colors.MAGENTA}🚀 Starting CaiRO Travel API server on port 3001{Colors.RESET}")
    uvicorn.run(app, host="0.0.0.0", port=3001) 