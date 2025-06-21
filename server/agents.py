import os
import logging
import re
import json
import random
from typing import List, Optional
from llm_utils import get_response_gemini, get_conversation_response_gemini, add_user_message_to_conversation
from google.genai import types

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
    logging.info(f"🛫 Searching flights from {source} to {destination} on {date}")
    logging.info(f"📋 Airlines: {', '.join(airlines)}")
    logging.info(f"🤖 Using model: {model}")
    
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

    logging.debug(f"🔍 Flight query: {flight_query}")
    
    try:
        # Use grounded search to get flight information
        logging.info("🔄 Making grounded API call for flight search...")
        
        response_text = get_response_gemini(
            model=model,
            user_query=flight_query,
            grounding=True,  # Enable grounding for Google Flights search
            thinking_budget=-1  # Use dynamic thinking for complex flight searches
        )
        
        logging.info("✅ Flight search completed successfully")
        logging.info(f"📊 Raw response length: {len(response_text)} characters")
        logging.debug(f"🔍 Raw flight response: {response_text}")
        
        # Clean up the response to extract just the JSON
        cleaned_response = clean_flight_response(response_text)
        logging.info(f"📊 Cleaned response length: {len(cleaned_response)} characters")
        logging.debug(f"🔍 Cleaned flight response: {cleaned_response}")
        
        # Parse the JSON and randomly select one flight
        try:
            flight_data = json.loads(cleaned_response)
            
            # Filter out airlines with empty flight lists
            non_empty_airlines = {airline: flights for airline, flights in flight_data.items() 
                                if flights and len(flights) > 0}
            
            if not non_empty_airlines:
                logging.error("❌ No airlines with available flights found")
                raise ValueError("No flights available from any airline")
            
            # Randomly select an airline
            selected_airline = random.choice(list(non_empty_airlines.keys()))
            logging.info(f"🎲 Randomly selected airline: {selected_airline}")
            
            # Randomly select a flight from the selected airline
            selected_flight = random.choice(non_empty_airlines[selected_airline])
            logging.info(f"🎲 Randomly selected flight: {selected_flight}")
            
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
            
            logging.info(f"✅ Final structured flight: {final_flight_json}")
            return json.dumps(final_flight_json, indent=2)
            
        except json.JSONDecodeError as e:
            logging.error(f"❌ Failed to parse flight JSON: {e}")
            logging.debug(f"🔍 Problematic JSON: {cleaned_response}")
            raise ValueError(f"Invalid JSON response from flight search: {e}")
        except KeyError as e:
            logging.error(f"❌ Missing expected key in flight data: {e}")
            logging.debug(f"🔍 Flight data structure: {flight_data}")
            raise ValueError(f"Unexpected flight data structure: {e}")
        except Exception as e:
            logging.error(f"❌ Error processing flight selection: {e}")
            raise
        
    except Exception as e:
        logging.error(f"❌ Error in search_flights: {e}")
        logging.error(f"🔍 Error type: {type(e).__name__}")
        logging.error(f"🔍 Error details: {str(e)}")
        raise

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
    logging.info(f"🏨 Searching hotels in {city}")
    logging.info(f"📅 Check-in: {check_in_date}, Check-out: {check_out_date}")
    logging.info(f"💰 Price range: ₹{price_min} - ₹{price_max} per night")
    logging.info(f"🤖 Using model: {model}")
    
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

    logging.debug(f"🔍 Hotel query: {hotel_query}")
    
    try:
        # Use grounded search to get hotel information
        logging.info("🔄 Making grounded API call for hotel search...")
        
        response_text = get_response_gemini(
            model=model,
            user_query=hotel_query,
            grounding=True,  # Enable grounding for Google Hotels search
            thinking_budget=-1  # Use dynamic thinking for complex hotel searches
        )
        
        logging.info("✅ Hotel search completed successfully")
        logging.info(f"📊 Raw response length: {len(response_text)} characters")
        logging.debug(f"🔍 Raw hotel response: {response_text}")
        
        # Clean up the response to extract just the JSONL
        cleaned_response = clean_hotel_response(response_text)
        logging.info(f"📊 Cleaned response length: {len(cleaned_response)} characters")
        logging.debug(f"🔍 Cleaned hotel response: {cleaned_response}")
        
        # Parse the JSONL and randomly select one hotel
        try:
            # Parse JSONL (each line is a separate JSON object)
            hotels = []
            for line in cleaned_response.strip().split('\n'):
                if line.strip():
                    hotel = json.loads(line.strip())
                    hotels.append(hotel)
            
            if not hotels:
                logging.error("❌ No hotels found in response")
                raise ValueError("No hotels available")
            
            # Randomly select a hotel
            selected_hotel = random.choice(hotels)
            logging.info(f"🎲 Randomly selected hotel: {selected_hotel}")
            
            # Structure the final JSON according to requirements
            final_hotel_json = {
                "name": selected_hotel["name"],
                "location": selected_hotel["location"], 
                "price": int(selected_hotel["price_per_night"]),
                "checkIn": check_in_date,
                "checkOut": check_out_date,
                "rating": float(selected_hotel["rating"])
            }
            
            logging.info(f"✅ Final structured hotel: {final_hotel_json}")
            return json.dumps(final_hotel_json, indent=2)
            
        except json.JSONDecodeError as e:
            logging.error(f"❌ Failed to parse hotel JSONL: {e}")
            logging.debug(f"🔍 Problematic JSONL: {cleaned_response}")
            raise ValueError(f"Invalid JSONL response from hotel search: {e}")
        except KeyError as e:
            logging.error(f"❌ Missing expected key in hotel data: {e}")
            logging.debug(f"🔍 Hotel data structure: {selected_hotel}")
            raise ValueError(f"Unexpected hotel data structure: {e}")
        except Exception as e:
            logging.error(f"❌ Error processing hotel selection: {e}")
            raise
        
    except Exception as e:
        logging.error(f"❌ Error in search_hotels: {e}")
        logging.error(f"🔍 Error type: {type(e).__name__}")
        logging.error(f"🔍 Error details: {str(e)}")
        raise

def clean_flight_response(response_text: str) -> str:
    """
    Clean up the flight search response to extract only the JSON data.
    Removes disclaimers and extra text that might appear with grounded responses.
    
    Args:
        response_text (str): Raw response from the model
        
    Returns:
        str: Cleaned JSON response
    """
    logging.debug("🧹 Cleaning flight response...")
    
    try:
        # Look for JSON content in the response
        # First try to find content within ```json blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            logging.debug("✅ Found JSON in code block")
        else:
            # Try to find JSON object directly in the text
            json_match = re.search(r'(\{[^{}]*\{[^{}]*\}[^{}]*\})', response_text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                logging.debug("✅ Found JSON object in text")
            else:
                # If no structured JSON found, return original response
                logging.warning("⚠️ No clear JSON structure found, returning original response")
                return response_text
        
        # Validate that it's proper JSON
        try:
            json.loads(json_content)
            logging.debug("✅ JSON validation successful")
            return json_content
        except json.JSONDecodeError:
            logging.warning("⚠️ JSON validation failed, returning original response")
            return response_text
            
    except Exception as e:
        logging.error(f"❌ Error cleaning response: {e}")
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
    logging.debug("🧹 Cleaning hotel response...")
    
    try:
        # Look for JSONL content in the response
        # First try to find content within ```jsonl blocks
        jsonl_match = re.search(r'```jsonl\s*(.*?)\s*```', response_text, re.DOTALL)
        if jsonl_match:
            jsonl_content = jsonl_match.group(1).strip()
            logging.debug("✅ Found JSONL in code block")
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
                logging.debug(f"✅ Found {len(jsonl_lines)} valid JSON lines")
            else:
                # If no JSONL found, return original response
                logging.warning("⚠️ No clear JSONL structure found, returning original response")
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
                    logging.warning(f"⚠️ Invalid JSON line skipped: {line[:50]}...")
                    continue
        
        if valid_lines:
            result = '\n'.join(valid_lines)
            logging.debug(f"✅ JSONL validation successful, {len(valid_lines)} valid lines")
            return result
        else:
            logging.warning("⚠️ No valid JSON lines found, returning original response")
            return response_text
            
    except Exception as e:
        logging.error(f"❌ Error cleaning response: {e}")
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
