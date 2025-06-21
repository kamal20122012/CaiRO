import os
import logging
import re
import json
import random
from typing import List, Optional
from llm_utils import get_response_gemini, get_conversation_response_gemini, add_user_message_to_conversation
from google.genai import types

# ANSI Color codes for colored logging
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Background colors for method identification
    FLIGHT_BG = '\033[44m'      # Blue background
    HOTEL_BG = '\033[42m'       # Green background
    
    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Method-specific prefixes
    FLIGHT_PREFIX = f'{FLIGHT_BG}{WHITE}{BOLD} ✈️  FLIGHTS {RESET}'
    HOTEL_PREFIX = f'{HOTEL_BG}{WHITE}{BOLD} 🏨 HOTELS  {RESET}'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

def search_flights(source: str, destination: str, date: str, airlines: List[str], model: str = "gemini-2.5-pro") -> str:
    """
    Search for flight information using grounded search with Google Flights.
    
    Args:
        source (str): Source city (e.g., "bangalore")
        destination (str): Destination city (e.g., "vizag")  
        date (str): Travel date (e.g., "27 June 2025")
        airlines (List[str]): List of airlines to search (e.g., ["indigo", "air india", "air india express", "vistara"])
        model (str): Gemini model to use (default: "gemini-2.5-pro")
        
    Returns:
        str: Flight information in JSON format
    """
    logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.CYAN}🛫 Searching flights from {source} to {destination} on {date}{Colors.RESET}")
    logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.BLUE}📋 Airlines: {', '.join(airlines)}{Colors.RESET}")
    logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.MAGENTA}🤖 Using model: {model}{Colors.RESET}")
    
    # Create the templatized query with more explicit instructions for grounded search
    airlines_str = ", ".join(airlines)
    
    flight_query = f"""Search Google Flights for current flight information:

Route: {source} to {destination}
Date: {date}
Airlines: {airlines_str}

IMPORTANT INSTRUCTIONS:
- Use live Google Flights search to get current pricing and availability
- Search from morning (early hours) to night (late hours) for comprehensive coverage
- Include all available flight times and current prices
- Format time in 24-hour format (HH:MM)
- Include price with currency symbol (₹ for INR)

OUTPUT FORMAT (JSON only, no explanatory text):
{{"airline_1": [{{"price": "₹4500", "departure_time": "06:25", "arrival_time": "08:30"}}, {{"price": "₹4200", "departure_time": "14:30", "arrival_time": "16:35"}}], "airline_2": [{{"price": "₹5000", "departure_time": "08:15", "arrival_time": "10:20"}}]}}

Example structure:
{{"indigo": [{{"price": "₹4500", "departure_time": "06:25", "arrival_time": "08:30"}}, {{"price": "₹4200", "departure_time": "14:30", "arrival_time": "16:35"}}], "air_india": [{{"price": "₹5000", "departure_time": "08:15", "arrival_time": "10:20"}}]}}

Search now and provide the live results in the exact JSON format above."""

    logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.CYAN}🔍 Flight query: {flight_query}{Colors.RESET}")
    
    # Retry mechanism: try up to 3 times before falling back to dummy data
    max_retries = 3
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            # Use grounded search to get flight information
            logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}🔄 Making grounded API call for flight search (attempt {attempt + 1}/{max_retries})...{Colors.RESET}")
            
            response_text = get_response_gemini(
                model=model,
                user_query=flight_query,
                grounding=True,  # Enable grounding for Google Flights search
                thinking_budget=-1  # Use dynamic thinking for complex flight searches
            )
            
            logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ Flight search completed successfully{Colors.RESET}")
            logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.BLUE}📊 Raw response length: {len(response_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.CYAN}🔍 Raw flight response: {response_text}{Colors.RESET}")
            
            # Clean up the response to extract just the JSON
            cleaned_response = clean_flight_response(response_text)
            logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.BLUE}📊 Cleaned response length: {len(cleaned_response)} characters{Colors.RESET}")
            logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.CYAN}🔍 Cleaned flight response: {cleaned_response}{Colors.RESET}")
            
            # Parse the JSON and randomly select one flight
            try:
                flight_data = json.loads(cleaned_response)
                
                # Filter out airlines with empty flight lists
                non_empty_airlines = {airline: flights for airline, flights in flight_data.items() 
                                    if flights and len(flights) > 0}
                
                if not non_empty_airlines:
                    logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ No airlines with available flights found{Colors.RESET}")
                    raise ValueError("No flights available from any airline")
                
                # Randomly select an airline
                selected_airline = random.choice(list(non_empty_airlines.keys()))
                logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.MAGENTA}🎲 Randomly selected airline: {selected_airline}{Colors.RESET}")
                
                # Randomly select a flight from the selected airline
                selected_flight = random.choice(non_empty_airlines[selected_airline])
                logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.MAGENTA}🎲 Randomly selected flight: {selected_flight}{Colors.RESET}")
                
                # Structure the final JSON according to requirements
                final_flight_json = {
                    "name": selected_airline,
                    "location": source,
                    "price": selected_flight["price"],
                    "date": date,
                    "departureTime": selected_flight["departure_time"],
                    "arrivalTime": selected_flight["arrival_time"],
                    "source": source,
                    "destination": destination
                }
                
                logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ Final structured flight: {final_flight_json}{Colors.RESET}")
                return json.dumps(final_flight_json, indent=2)
                
            except json.JSONDecodeError as e:
                logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ Failed to parse flight JSON: {e}{Colors.RESET}")
                logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.RED}🔍 Problematic JSON: {cleaned_response}{Colors.RESET}")
                raise ValueError(f"Invalid JSON response from flight search: {e}")
            except KeyError as e:
                logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ Missing expected key in flight data: {e}{Colors.RESET}")
                logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.RED}🔍 Flight data structure: {flight_data}{Colors.RESET}")
                raise ValueError(f"Unexpected flight data structure: {e}")
            except Exception as e:
                logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ Error processing flight selection: {e}{Colors.RESET}")
                raise
            
        except Exception as e:
            last_exception = e
            logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ Error in search_flights attempt {attempt + 1}: {e}{Colors.RESET}")
            logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            
            if attempt < max_retries - 1:
                logging.warning(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}🔄 Retrying flight search (attempt {attempt + 2}/{max_retries})...{Colors.RESET}")
            else:
                logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ All {max_retries} attempts failed for flight search{Colors.RESET}")
                logging.warning(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}🔄 Using fallback dummy flight data{Colors.RESET}")
    
    # Return dummy flight data as fallback (only reached if all retries failed)
    dummy_flight_data = {
        "name": "IndiGo",
        "location": source,
        "price": "₹4,500",
        "date": date,
        "departureTime": "08:30",
        "arrivalTime": "10:45",
        "source": source,
        "destination": destination
    }
    
    logging.info(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ Fallback flight data: {dummy_flight_data}{Colors.RESET}")
    return json.dumps(dummy_flight_data, indent=2)

def search_hotels(city: str, 
                  check_in_date: str, check_out_date: str,
                  price_min: int, price_max: int, model: str = "gemini-2.5-pro") -> str:
    """
    Search for hotel information using grounded search with Google Hotels.
    
    Args:
        city (str): City name (e.g., "bangalore")
        check_in_date (str): Check-in date (e.g., "24 Jun 2025")
        check_out_date (str): Check-out date (e.g., "29 Jun 2025")
        price_min (int): Minimum price per night (e.g., 1000)
        price_max (int): Maximum price per night (e.g., 2000)
        model (str): Gemini model to use (default: "gemini-2.5-pro")
        
    Returns:
        str: Hotel information in JSONL format
    """
    logging.info(f"{Colors.HOTEL_PREFIX} {Colors.CYAN}🏨 Searching hotels in {city}{Colors.RESET}")
    logging.info(f"{Colors.HOTEL_PREFIX} {Colors.BLUE}📅 Check-in: {check_in_date}, Check-out: {check_out_date}{Colors.RESET}")
    logging.info(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}💰 Price range: ₹{price_min} - ₹{price_max} per night{Colors.RESET}")
    logging.info(f"{Colors.HOTEL_PREFIX} {Colors.MAGENTA}🤖 Using model: {model}{Colors.RESET}")
    
    # Create the templatized query with explicit instructions for grounded search
    hotel_query = f"""Search Google Hotels for current hotel information:

Location: {city}
Price Range: ₹{price_min} to ₹{price_max} per night

IMPORTANT INSTRUCTIONS:
- Use live Google Hotels search to get current pricing and availability
- Search for hotels within the specified price range only
- Include hotel ratings (out of 5), exact location/area within the city
- Include price per night with currency symbol (₹ for INR)
- Focus on well-reviewed hotels with good ratings
- Include specific area/neighborhood information within the city

OUTPUT FORMAT (JSONL only, no explanatory text):
Each line should be a separate JSON object with this exact structure:
{{"name": "Hotel Name", "price_per_night": "1500", "rating": "4.2", "location": "Specific Area, City"}}

Example:
{{"name": "Hotel Sigma Suites", "price_per_night": "1283", "rating": "4.2", "location": "Gandhi Nagar, Bangalore"}}
{{"name": "Magaji Residency", "price_per_night": "1046", "rating": "3.9", "location": "Jayanagar, Bangalore"}}

Search now and provide live results in exact JSONL format above."""

    logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.CYAN}🔍 Hotel query: {hotel_query}{Colors.RESET}")
    
    # Retry mechanism: try up to 3 times before falling back to dummy data
    max_retries = 3
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            # Use grounded search to get hotel information
            logging.info(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}🔄 Making grounded API call for hotel search (attempt {attempt + 1}/{max_retries})...{Colors.RESET}")
            
            response_text = get_response_gemini(
                model=model,
                user_query=hotel_query,
                grounding=True,  # Enable grounding for Google Hotels search
                thinking_budget=-1  # Use dynamic thinking for complex hotel searches
            )
            
            logging.info(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ Hotel search completed successfully{Colors.RESET}")
            logging.info(f"{Colors.HOTEL_PREFIX} {Colors.BLUE}📊 Raw response length: {len(response_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.CYAN}🔍 Raw hotel response: {response_text}{Colors.RESET}")
            
            # Clean up the response to extract just the JSONL
            cleaned_response = clean_hotel_response(response_text)
            logging.info(f"{Colors.HOTEL_PREFIX} {Colors.BLUE}📊 Cleaned response length: {len(cleaned_response)} characters{Colors.RESET}")
            logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.CYAN}🔍 Cleaned hotel response: {cleaned_response}{Colors.RESET}")
            
            # Parse the JSONL and randomly select one hotel
            try:
                # Parse JSONL (each line is a separate JSON object)
                hotels = []
                for line in cleaned_response.strip().split('\n'):
                    if line.strip():
                        hotel = json.loads(line.strip())
                        hotels.append(hotel)
                
                if not hotels:
                    logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ No hotels found in response{Colors.RESET}")
                    raise ValueError("No hotels available")
                
                # Randomly select a hotel
                selected_hotel = random.choice(hotels)
                logging.info(f"{Colors.HOTEL_PREFIX} {Colors.MAGENTA}🎲 Randomly selected hotel: {selected_hotel}{Colors.RESET}")
                
                # Structure the final JSON according to requirements
                final_hotel_json = {
                    "name": selected_hotel["name"],
                    "location": selected_hotel["location"], 
                    "price": int(selected_hotel["price_per_night"]),
                    "checkIn": check_in_date,
                    "checkOut": check_out_date,
                    "rating": float(selected_hotel["rating"])
                }
                
                logging.info(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ Final structured hotel: {final_hotel_json}{Colors.RESET}")
                return json.dumps(final_hotel_json, indent=2)
                
            except json.JSONDecodeError as e:
                logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ Failed to parse hotel JSONL: {e}{Colors.RESET}")
                logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.RED}🔍 Problematic JSONL: {cleaned_response}{Colors.RESET}")
                raise ValueError(f"Invalid JSONL response from hotel search: {e}")
            except KeyError as e:
                logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ Missing expected key in hotel data: {e}{Colors.RESET}")
                logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.RED}🔍 Hotel data structure: {selected_hotel}{Colors.RESET}")
                raise ValueError(f"Unexpected hotel data structure: {e}")
            except Exception as e:
                logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ Error processing hotel selection: {e}{Colors.RESET}")
                raise
            
        except Exception as e:
            last_exception = e
            logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ Error in search_hotels attempt {attempt + 1}: {e}{Colors.RESET}")
            logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            
            if attempt < max_retries - 1:
                logging.warning(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}🔄 Retrying hotel search (attempt {attempt + 2}/{max_retries})...{Colors.RESET}")
            else:
                logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ All {max_retries} attempts failed for hotel search{Colors.RESET}")
                logging.warning(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}🔄 Using fallback dummy hotel data{Colors.RESET}")
    
    # Return dummy hotel data as fallback (only reached if all retries failed)
    dummy_hotel_data = {
        "name": "Grand Palace Hotel",
        "location": f"City Center, {city}",
        "price": random.randint(price_min, price_max),
        "checkIn": check_in_date,
        "checkOut": check_out_date,
        "rating": 4.2
    }
    
    logging.info(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ Fallback hotel data: {dummy_hotel_data}{Colors.RESET}")
    return json.dumps(dummy_hotel_data, indent=2)

def clean_flight_response(response_text: str) -> str:
    """
    Clean up the flight search response to extract only the JSON data.
    Removes disclaimers and extra text that might appear with grounded responses.
    
    Args:
        response_text (str): Raw response from the model
        
    Returns:
        str: Cleaned JSON response
    """
    logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}🧹 Cleaning flight response...{Colors.RESET}")
    
    try:
        # Look for JSON content in the response
        # First try to find content within ```json blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ Found JSON in code block{Colors.RESET}")
        else:
            # Try to find JSON object directly in the text
            json_match = re.search(r'(\{[^{}]*\{[^{}]*\}[^{}]*\})', response_text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ Found JSON object in text{Colors.RESET}")
            else:
                # If no structured JSON found, return original response
                logging.warning(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}⚠️ No clear JSON structure found, returning original response{Colors.RESET}")
                return response_text
        
        # Validate that it's proper JSON
        try:
            json.loads(json_content)
            logging.debug(f"{Colors.FLIGHT_PREFIX} {Colors.GREEN}✅ JSON validation successful{Colors.RESET}")
            return json_content
        except json.JSONDecodeError:
            logging.warning(f"{Colors.FLIGHT_PREFIX} {Colors.YELLOW}⚠️ JSON validation failed, returning original response{Colors.RESET}")
            return response_text
            
    except Exception as e:
        logging.error(f"{Colors.FLIGHT_PREFIX} {Colors.RED}❌ Error cleaning response: {e}{Colors.RESET}")
        return response_text

def clean_hotel_response(response_text: str) -> str:
    """
    Clean up the hotel search response to extract only the JSONL data.
    Removes disclaimers and extra text that might appear with grounded responses.
    
    Args:
        response_text (str): Raw response from the model
        
    Returns:
        str: Cleaned JSONL response
    """
    logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}🧹 Cleaning hotel response...{Colors.RESET}")
    
    try:
        # Look for JSONL content in the response
        # First try to find content within ```jsonl blocks
        jsonl_match = re.search(r'```jsonl\s*(.*?)\s*```', response_text, re.DOTALL)
        if jsonl_match:
            jsonl_content = jsonl_match.group(1).strip()
            logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ Found JSONL in code block{Colors.RESET}")
        else:
            # Look for lines that appear to be JSON objects
            lines = response_text.split('\n')
            jsonl_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('{"') and line.endswith('}'):
                    # Validate it's proper JSON
                    try:
                        json.loads(line)
                        jsonl_lines.append(line)
                    except json.JSONDecodeError:
                        continue
            
            if jsonl_lines:
                jsonl_content = '\n'.join(jsonl_lines)
                logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ Found {len(jsonl_lines)} valid JSON lines{Colors.RESET}")
            else:
                # If no JSONL found, return original response
                logging.warning(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}⚠️ No clear JSONL structure found, returning original response{Colors.RESET}")
                return response_text
        
        # Validate each line is proper JSON
        lines = jsonl_content.split('\n')
        valid_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                try:
                    json.loads(line)
                    valid_lines.append(line)
                except json.JSONDecodeError:
                    logging.warning(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}⚠️ Invalid JSON line skipped: {line[:50]}...{Colors.RESET}")
                    continue
        
        if valid_lines:
            result = '\n'.join(valid_lines)
            logging.debug(f"{Colors.HOTEL_PREFIX} {Colors.GREEN}✅ JSONL validation successful, {len(valid_lines)} valid lines{Colors.RESET}")
            return result
        else:
            logging.warning(f"{Colors.HOTEL_PREFIX} {Colors.YELLOW}⚠️ No valid JSON lines found, returning original response{Colors.RESET}")
            return response_text
            
    except Exception as e:
        logging.error(f"{Colors.HOTEL_PREFIX} {Colors.RED}❌ Error cleaning response: {e}{Colors.RESET}")
        return response_text

# Example usage:
if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        exit(1)
    
    # Test the new grounded flight search
    print("🧪 Testing new grounded flight search...")
    try:
        result = search_flights(
            source="bangalore",
            destination="vizag",
            date="27 June 2025",
            airlines=["indigo", "air india", "air india express", "vistara"]
        )
        print("\n✅ Flight Search Results:")
        print(result)
    except Exception as e:
        print(f"❌ Error searching flights: {e}")
    
    print("\n" + "="*50)
    
    # Test the new grounded hotel search
    print("🧪 Testing new grounded hotel search...")
    try:
        result = search_hotels(
            city="bangalore",
            check_in_date="24 Jun 2025",
            check_out_date="29 Jun 2025",
            price_min=1000,
            price_max=2000
        )
        print("\n✅ Hotel Search Results:")
        print(result)
    except Exception as e:
        print(f"❌ Error searching hotels: {e}")
    
    # Legacy aviationstack example (commented out)
    # data = search_flights_aviationstack(
    #     access_key='3f17cc261524dbff5ee71a95d1df2175',
    #     dep_iata='DEL',
    #     arr_iata='BOM',
    #     date_str='2025-06-22'
    # )
    # print(data)
