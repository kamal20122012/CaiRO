from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
import json
import os

# Import the functions from existing modules
from create_itnr import create_itinerary, update_itinerary
from agents import search_flights, search_hotels
from suggestions import suggest_activities

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

# Pydantic model for update request body
class UpdateItineraryRequest(BaseModel):
    user_request: str

# Pydantic model for activity suggestions request
class ActivitySuggestionsRequest(BaseModel):
    city: str

# Root endpoint
@app.get("/")
async def root():
    logging.info(f"{Colors.API_PREFIX} {Colors.CYAN}🏠 Root endpoint accessed{Colors.RESET}")
    return {
        "message": "Welcome to CaiRO Travel API",
        "endpoints": {
            "generate_itinerary": "/api/itinerary/generate",
            "update_itinerary": "/api/itinerary/update",
            "get_latest_itinerary": "/api/itinerary/latest",
            "suggest_activities": "/api/itinerary/suggest/activities",
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
            
            # Clean the response for client compatibility
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}🧹 Cleaning itinerary response for client compatibility{Colors.RESET}")
            cleaned_itinerary = clean_itinerary_for_client(parsed_result)
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}✅ Itinerary cleaned and ready for client{Colors.RESET}")
            
            # Save the cleaned itinerary to file for later access
            saved_file_path = save_itinerary_to_file(cleaned_itinerary, request)
            
            return {"status": "success", "data": cleaned_itinerary}
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ Result is not valid JSON, returning as text{Colors.RESET}")
            return {"status": "success", "data": result}
            
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error creating itinerary: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error creating itinerary: {str(e)}")

# Update itinerary endpoint
@app.post("/api/itinerary/update")
async def update_itinerary_endpoint(request: UpdateItineraryRequest):
    """
    Update an existing itinerary based on user request.
    
    Args:
        UpdateItineraryRequest: Request containing user's update request
    
    Returns:
        JSON response with the updated itinerary
    """
    try:
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🔄 Updating itinerary based on user request{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.BLUE}📝 Update request: {request.user_request}{Colors.RESET}")
        
        # Load the latest saved itinerary
        file_path = os.path.join("saved_itineraries", "latest_itinerary.json")
        
        if not os.path.exists(file_path):
            logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ No saved itinerary found for update{Colors.RESET}")
            raise HTTPException(status_code=404, detail="No saved itinerary found. Please generate an itinerary first.")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Extract the itinerary data from saved file
        itinerary_data = saved_data.get('itinerary', {})
        original_metadata = saved_data.get('metadata', {})
        
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.BLUE}📖 Loaded existing itinerary from {file_path}{Colors.RESET}")
        
        # Convert itinerary data back to JSON string for the update function
        itinerary_json_str = json.dumps(itinerary_data, indent=2)
        
        # Call the update function
        result = update_itinerary(
            itinerary_json=itinerary_json_str,
            user_query=request.user_request,
            model="gemini-2.0-flash"
        )
        
        # Try to parse the result as JSON to validate it
        try:
            parsed_result = json.loads(result)
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}✅ Itinerary updated successfully{Colors.RESET}")
            
            # Clean the response for client compatibility
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}🧹 Cleaning updated itinerary response for client compatibility{Colors.RESET}")
            cleaned_itinerary = clean_itinerary_for_client(parsed_result)
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}✅ Updated itinerary cleaned and ready for client{Colors.RESET}")
            
            # Save the updated itinerary to file (preserve original metadata)
            updated_save_data = {
                "metadata": original_metadata,
                "itinerary": cleaned_itinerary
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_save_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}💾 Updated itinerary saved to {file_path}{Colors.RESET}")
            
            return {"status": "success", "data": cleaned_itinerary}
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ Update result is not valid JSON, returning as text{Colors.RESET}")
            return {"status": "success", "data": result}
            
    except FileNotFoundError:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Saved itinerary file not found{Colors.RESET}")
        raise HTTPException(status_code=404, detail="No saved itinerary found. Please generate an itinerary first.")
    except json.JSONDecodeError:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error parsing saved itinerary file{Colors.RESET}")
        raise HTTPException(status_code=500, detail="Error parsing saved itinerary file")
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error updating itinerary: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error updating itinerary: {str(e)}")

# Suggest activities endpoint
@app.post("/api/itinerary/suggest/activities")
async def suggest_activities_endpoint(request: ActivitySuggestionsRequest):
    """
    Get activity suggestions for a given city using AI.
    
    Args:
        ActivitySuggestionsRequest: Request containing the city name
    
    Returns:
        JSON response with a list of activity suggestions
    """
    try:
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🎯 Generating activity suggestions for {request.city}{Colors.RESET}")
        
        activities = suggest_activities(request.city)
        
        if activities:
            logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}✅ Generated {len(activities)} activity suggestions for {request.city}{Colors.RESET}")
            return {"status": "success", "data": {"city": request.city, "activities": activities}}
        else:
            logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ No activity suggestions generated for {request.city}{Colors.RESET}")
            return {"status": "success", "data": {"city": request.city, "activities": []}}
            
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error generating activity suggestions: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error generating activity suggestions: {str(e)}")

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

# Get saved itinerary endpoint
@app.get("/api/itinerary/latest")
async def get_latest_itinerary():
    """
    Retrieve the latest saved itinerary from file.
    
    Returns:
        JSON response with the saved itinerary data
    """
    try:
        file_path = os.path.join("saved_itineraries", "latest_itinerary.json")
        
        if not os.path.exists(file_path):
            logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ No saved itinerary found{Colors.RESET}")
            raise HTTPException(status_code=404, detail="No saved itinerary found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}📖 Retrieved saved itinerary from {file_path}{Colors.RESET}")
        return {"status": "success", "data": saved_data}
        
    except json.JSONDecodeError:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error parsing saved itinerary file{Colors.RESET}")
        raise HTTPException(status_code=500, detail="Error parsing saved itinerary file")
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error retrieving saved itinerary: {e}{Colors.RESET}")
        raise HTTPException(status_code=500, detail=f"Error retrieving saved itinerary: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    logging.info(f"{Colors.API_PREFIX} {Colors.GREEN}💚 Health check accessed{Colors.RESET}")
    return {"status": "healthy", "message": "CaiRO Travel API is running"}

def save_itinerary_to_file(itinerary_data: dict, request_data: TripFormOutput) -> str:
    """
    Save the itinerary data to a JSON file for later access.
    
    Args:
        itinerary_data (dict): The cleaned itinerary data
        request_data (TripFormOutput): Original request data for metadata
        
    Returns:
        str: Path to the saved file
    """
    try:
        # Create a data directory if it doesn't exist
        data_dir = "saved_itineraries"
        os.makedirs(data_dir, exist_ok=True)
        
        # Create filename with destination and timestamp for uniqueness
        filename = "latest_itinerary.json"
        file_path = os.path.join(data_dir, filename)
        
        # Prepare data to save (include both itinerary and request metadata)
        save_data = {
            "metadata": {
                "destination": request_data.destination,
                "source": request_data.source,
                "departure_date": request_data.departureDate,
                "arrival_date": request_data.arrivalDate,
                "days": request_data.days,
                "trip_theme": request_data.trip_theme,
                "user_mood": request_data.user_mood,
                "vibe_keywords": request_data.vibe_keywords,
                "activities": request_data.activities,
                "avoid": request_data.avoid,
                "been_here_before": request_data.been_here_before
            },
            "itinerary": itinerary_data
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.GREEN}💾 Itinerary saved to {file_path}{Colors.RESET}")
        return file_path
        
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_API_PREFIX} {Colors.RED}❌ Error saving itinerary to file: {e}{Colors.RESET}")
        return ""

def clean_itinerary_for_client(itinerary_data: dict) -> dict:
    """
    Clean the itinerary data to match client expectations.
    
    - Remove 'category' and 'meal_type' fields from activities
    - Map 'notes' to 'description' for client compatibility
    
    Args:
        itinerary_data (dict): Raw itinerary data with internal structure
        
    Returns:
        dict: Cleaned itinerary data compatible with client
    """
    if not isinstance(itinerary_data, dict) or 'days' not in itinerary_data:
        logging.warning(f"{Colors.ITINERARY_API_PREFIX} {Colors.YELLOW}⚠️ Invalid itinerary data structure, returning as-is{Colors.RESET}")
        return itinerary_data
    
    cleaned_data = itinerary_data.copy()
    
    total_activities_cleaned = 0
    categories_removed = set()
    meal_types_removed = set()
    
    # Clean each day's activities
    for day_index, day in enumerate(cleaned_data.get('days', [])):
        if 'activities' not in day:
            continue
            
        cleaned_activities = []
        for activity_index, activity in enumerate(day['activities']):
            if not isinstance(activity, dict):
                cleaned_activities.append(activity)
                continue
                
            # Create cleaned activity
            cleaned_activity = {}
            
            # Track what we're removing for logging
            removed_fields = []
            
            # Copy all fields except the ones we want to remove/transform
            for key, value in activity.items():
                if key in ['category', 'meal_type']:
                    # Track removed fields for logging
                    removed_fields.append(f"{key}={value}")
                    if key == 'category':
                        categories_removed.add(value)
                    elif key == 'meal_type':
                        meal_types_removed.add(value)
                    continue
                elif key == 'notes':
                    # Map notes to description for client compatibility
                    cleaned_activity['description'] = value
                    removed_fields.append("notes→description")
                else:
                    # Keep all other fields as-is
                    cleaned_activity[key] = value
            
            # Ensure description exists (fallback to empty string if no notes)
            if 'description' not in cleaned_activity:
                cleaned_activity['description'] = ''
                
            cleaned_activities.append(cleaned_activity)
            total_activities_cleaned += 1
            
            # Log detailed cleaning for first few activities
            if total_activities_cleaned <= 3 and removed_fields:
                logging.debug(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🧹 Day {day['day']} Activity {activity_index + 1}: Cleaned '{activity.get('name', 'Unknown')}' - Removed: {', '.join(removed_fields)}{Colors.RESET}")
        
        day['activities'] = cleaned_activities
    
    # Log summary
    logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.BLUE}📊 Cleaned {total_activities_cleaned} activities across {len(cleaned_data.get('days', []))} days{Colors.RESET}")
    if categories_removed:
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🏷️ Categories removed: {', '.join(sorted(categories_removed))}{Colors.RESET}")
    if meal_types_removed:
        logging.info(f"{Colors.ITINERARY_API_PREFIX} {Colors.CYAN}🍽️ Meal types removed: {', '.join(sorted(meal_types_removed))}{Colors.RESET}")
    
    return cleaned_data

if __name__ == "__main__":
    import uvicorn
    logging.info(f"{Colors.API_PREFIX} {Colors.MAGENTA}🚀 Starting CaiRO Travel API server on port 3001{Colors.RESET}")
    uvicorn.run(app, host="0.0.0.0", port=3001) 