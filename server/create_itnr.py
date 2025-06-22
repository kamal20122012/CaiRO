import os
import logging
import json
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional
from google.genai import types
from prompt_lib import (
    itnr_1, itnr_3,
    itnr_2_nightlife, itnr_2_family, itnr_2_luxury, itnr_2_backpacker, itnr_2_cultural,
    itnr_2_adventure, itnr_2_romantic, itnr_2_business, itnr_2_wellness, itnr_2_foodie
)
from llm_utils import get_conversation_response_gemini, add_user_message_to_conversation
from db_init import find_best_persona_match

# ANSI Color codes for colored logging
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Background colors for method identification
    ITINERARY_BG = '\033[45m'   # Magenta background
    
    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Method-specific prefix
    ITINERARY_PREFIX = f'{ITINERARY_BG}{WHITE}{BOLD} 🗺️  ITINERARY {RESET}'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from a response that might be wrapped in markdown code blocks.
    
    Args:
        response_text (str): The response text that might contain JSON wrapped in ```json blocks
        
    Returns:
        str: The extracted JSON string
    """
    # Try to extract JSON from ```json code blocks
    json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    # Try to extract JSON from ``` code blocks
    code_match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
    if code_match:
        potential_json = code_match.group(1).strip()
        # Check if it looks like JSON (starts with { or [)
        if potential_json.startswith(('{', '[')):
            return potential_json
    
    # If no code blocks found, return as is
    return response_text.strip()


def get_persona_prompt(persona_key: str) -> str:
    """Get the appropriate persona prompt based on the persona key"""
    prompt_mapping = {
        "itnr_2_nightlife": itnr_2_nightlife,
        "itnr_2_family": itnr_2_family,
        "itnr_2_luxury": itnr_2_luxury,
        "itnr_2_backpacker": itnr_2_backpacker,
        "itnr_2_cultural": itnr_2_cultural,
        "itnr_2_adventure": itnr_2_adventure,
        "itnr_2_romantic": itnr_2_romantic,
        "itnr_2_business": itnr_2_business,
        "itnr_2_wellness": itnr_2_wellness,
        "itnr_2_foodie": itnr_2_foodie
    }
    
    return prompt_mapping.get(persona_key, itnr_2_cultural)

def create_itinerary(city_name: str, user_pref: str, n_days: int, model: str = "gemini-2.0-flash") -> str:
    """
    Creates an optimized itinerary using three sequential prompts with Gemini API.
    
    Args:
        city_name (str): Name of the city for the trip
        user_pref (str): User preferences for the trip
        n_days (int): Number of days for the itinerary
        model (str): Gemini model to use (default: "gemini-2.0-flash")
        
    Returns:
        str: Final optimized itinerary in JSON format
    """
    
    # Initialize timing tracking
    start_time = time.time()
    api_call_times = []
    
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🚀 Starting itinerary creation for {city_name} ({n_days} days){Colors.RESET}")
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📋 User preferences: {user_pref}{Colors.RESET}")
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.MAGENTA}🤖 Using model: {model}{Colors.RESET}")
    
    # Step 0: Select the best matching persona based on user preferences
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🎯 Step 0/5: Selecting best matching persona...{Colors.RESET}")
    try:
        selected_persona_key = find_best_persona_match(user_pref)
        selected_prompt = get_persona_prompt(selected_persona_key)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Selected persona: {selected_persona_key}{Colors.RESET}")
    except Exception as e:
        logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Error in persona selection: {e}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Falling back to cultural persona{Colors.RESET}")
        selected_persona_key = "itnr_2_cultural"
        selected_prompt = itnr_2_cultural
    
    try:
        # Format the first prompt with city name
        prompt_1 = itnr_1.format(city_name=city_name)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 1/5: Formatted first prompt for attractions categorization{Colors.RESET}")
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Prompt 1 content: {prompt_1}{Colors.RESET}")
        
        # Start conversation with first prompt
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Adding first prompt to conversation history...{Colors.RESET}")
        conversation_history = add_user_message_to_conversation([], prompt_1)
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after adding prompt 1: {len(conversation_history)}{Colors.RESET}")
        
        # Generate response for first prompt (attractions categorization)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Making API call 1/3: Getting attractions categorization...{Colors.RESET}")
        api_call_1_start = time.time()
        try:
            response_1_text, conversation_history = get_conversation_response_gemini(
                model=model,
                conversation_history=conversation_history,
                grounding=True  # Enable grounding for better attraction data
            )
            api_call_1_end = time.time()
            api_call_1_duration = api_call_1_end - api_call_1_start
            api_call_times.append(("API Call 1 (Attractions categorization)", api_call_1_duration))
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 1/5 completed: Received attractions categorization{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ API Call 1 duration: {api_call_1_duration:.2f} seconds{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Response 1 length: {len(response_1_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Response 1 content: {response_1_text}{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after response 1: {len(conversation_history)}{Colors.RESET}")
                
        except Exception as e:
            api_call_1_end = time.time()
            api_call_1_duration = api_call_1_end - api_call_1_start
            api_call_times.append(("API Call 1 (Failed)", api_call_1_duration))
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in API call 1/3: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ API Call 1 failed after: {api_call_1_duration:.2f} seconds{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            raise
        
        # Format and add second prompt with user preferences and number of days using selected persona
        prompt_2 = selected_prompt.format(user_pref=user_pref, n_days=n_days)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 2/5: Formatted second prompt for initial itinerary creation (using {selected_persona_key}){Colors.RESET}")
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Prompt 2 content: {prompt_2}{Colors.RESET}")
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Adding second prompt to conversation history...{Colors.RESET}")
        conversation_history = add_user_message_to_conversation(conversation_history, prompt_2)
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after adding prompt 2: {len(conversation_history)}{Colors.RESET}")
        
        # Generate response for second prompt (initial itinerary)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Making API call 2/3: Creating initial itinerary...{Colors.RESET}")
        api_call_2_start = time.time()
        try:
            response_2_text, conversation_history = get_conversation_response_gemini(
                model=model,
                conversation_history=conversation_history,
                grounding=False  # No grounding needed for itinerary creation
            )
            api_call_2_end = time.time()
            api_call_2_duration = api_call_2_end - api_call_2_start
            api_call_times.append(("API Call 2 (Initial itinerary)", api_call_2_duration))
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 2/5 completed: Received initial itinerary{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ API Call 2 duration: {api_call_2_duration:.2f} seconds{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Response 2 length: {len(response_2_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Response 2 content: {response_2_text}{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after response 2: {len(conversation_history)}{Colors.RESET}")
                
        except Exception as e:
            api_call_2_end = time.time()
            api_call_2_duration = api_call_2_end - api_call_2_start
            api_call_times.append(("API Call 2 (Failed)", api_call_2_duration))
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in API call 2/3: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ API Call 2 failed after: {api_call_2_duration:.2f} seconds{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            raise
        
        # Add third prompt for optimization
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 3/5: Added third prompt for location-based optimization{Colors.RESET}")
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Prompt 3 content: {itnr_3}{Colors.RESET}")
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Adding third prompt to conversation history...{Colors.RESET}")
        conversation_history = add_user_message_to_conversation(conversation_history, itnr_3)
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after adding prompt 3: {len(conversation_history)}{Colors.RESET}")
        
        # Generate final optimized response
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Making API call 3/3: Optimizing itinerary based on locations...{Colors.RESET}")
        api_call_3_start = time.time()
        try:
            response_3_text, conversation_history = get_conversation_response_gemini(
                model=model,
                conversation_history=conversation_history,
                grounding=False  # No grounding needed for optimization
            )
            api_call_3_end = time.time()
            api_call_3_duration = api_call_3_end - api_call_3_start
            api_call_times.append(("API Call 3 (Optimization)", api_call_3_duration))
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 3/5 completed: Received final optimized itinerary{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ API Call 3 duration: {api_call_3_duration:.2f} seconds{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Response 3 length: {len(response_3_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Response 3 content: {response_3_text}{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Final conversation history length: {len(conversation_history)}{Colors.RESET}")
            
            # Extract JSON from final response (handle ```json code blocks)
            final_json = extract_json_from_response(response_3_text)
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔧 Extracted JSON from final response{Colors.RESET}")
            
            # Try to validate final JSON
            try:
                json.loads(final_json)
                logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Final response is valid JSON{Colors.RESET}")
            except json.JSONDecodeError as e:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Final response is not valid JSON: {e}{Colors.RESET}")
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔍 Final response raw text: {repr(final_json)}{Colors.RESET}")
                # Return the extracted content anyway, it might still be useful
                
        except Exception as e:
            api_call_3_end = time.time()
            api_call_3_duration = api_call_3_end - api_call_3_start
            api_call_times.append(("API Call 3 (Failed)", api_call_3_duration))
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in API call 3/3: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ API Call 3 failed after: {api_call_3_duration:.2f} seconds{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            raise
        
        # Calculate total time and log summary
        end_time = time.time()
        total_duration = end_time - start_time
        total_api_time = sum(duration for _, duration in api_call_times)
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}🎉 Itinerary creation process completed successfully!{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 TIMING SUMMARY{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        
        for call_name, duration in api_call_times:
            percentage = (duration / total_api_time) * 100 if total_api_time > 0 else 0
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}⏱️ {call_name}: {duration:.2f}s ({percentage:.1f}%){Colors.RESET}")
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'-' * 60}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}🔄 Total API call time: {total_api_time:.2f}s{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}⏱️ Total execution time: {total_duration:.2f}s{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}📈 API efficiency: {(total_api_time/total_duration)*100:.1f}% (API time / total time){Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        
        # Step 4: Add images to activities
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🖼️ Step 4/5: Adding images to activities...{Colors.RESET}")
        image_start_time = time.time()
        
        try:
            final_json_with_images = add_images_to_activities(final_json, destination=city_name)
            image_end_time = time.time()
            image_duration = image_end_time - image_start_time
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 4/5 completed: Images added to activities{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ Image processing duration: {image_duration:.2f} seconds{Colors.RESET}")
            
            # Update total duration to include image processing
            total_duration_with_images = end_time - start_time + image_duration
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}⏱️ Total execution time (with images): {total_duration_with_images:.2f}s{Colors.RESET}")
            
            return final_json_with_images
            
        except Exception as e:
            image_end_time = time.time()
            image_duration = image_end_time - image_start_time
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error adding images to activities: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ Image processing failed after: {image_duration:.2f} seconds{Colors.RESET}")
            logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Returning itinerary without images{Colors.RESET}")
            
            return final_json
        
    except Exception as e:
        # Calculate time even on error
        end_time = time.time()
        total_duration = end_time - start_time
        total_api_time = sum(duration for _, duration in api_call_times)
        
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Critical error in create_itinerary function: {e}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error repr: {repr(e)}{Colors.RESET}")
        
        # Log timing summary even on error
        if api_call_times:
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}{'=' * 60}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}📊 TIMING SUMMARY (FAILED EXECUTION){Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}{'=' * 60}{Colors.RESET}")
            
            for call_name, duration in api_call_times:
                percentage = (duration / total_api_time) * 100 if total_api_time > 0 else 0
                logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ {call_name}: {duration:.2f}s ({percentage:.1f}%){Colors.RESET}")
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}{'-' * 60}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔄 Total API call time: {total_api_time:.2f}s{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ Total execution time: {total_duration:.2f}s{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}{'=' * 60}{Colors.RESET}")
        
        raise


def update_itinerary(itinerary_json: str, user_query: str, destination: str = "", model: str = "gemini-2.5-pro") -> str:
    """
    Updates an existing itinerary based on user query using Gemini API.
    
    Args:
        itinerary_json (str): The complete itinerary JSON to be updated
        user_query (str): User's request for changes to the itinerary
        destination (str): Destination/city name for image search (optional, will try to extract from itinerary)
        model (str): Gemini model to use (default: "gemini-2.0-flash")
        
    Returns:
        str: Updated itinerary in JSON format with same structure
    """
    
    # Initialize timing tracking
    start_time = time.time()
    
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔄 Starting itinerary update process{Colors.RESET}")
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📝 User query: {user_query}{Colors.RESET}")
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.MAGENTA}🤖 Using model: {model}{Colors.RESET}")
    
    try:
        # Create the update prompt
        update_prompt = f"""You are given a trip itinerary as follows:
{itinerary_json}
there will be a user request, based on which you have to make changes in the itinerary. Make sure to change only the affected cells, keep the remaining as it is
<user_query>
{user_query}
</user_query>"""
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Formatted update prompt{Colors.RESET}")
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Update prompt content: {update_prompt}{Colors.RESET}")
        
        # Start conversation with update prompt
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Adding update prompt to conversation history...{Colors.RESET}")
        conversation_history = add_user_message_to_conversation([], update_prompt)
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Conversation history length after adding update prompt: {len(conversation_history)}{Colors.RESET}")
        
        # Generate updated itinerary response
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Making API call for itinerary update...{Colors.RESET}")
        api_call_start = time.time()
        try:
            response_text, conversation_history = get_conversation_response_gemini(
                model=model,
                conversation_history=conversation_history,
                grounding=False  # No grounding needed for itinerary updates
            )
            api_call_end = time.time()
            api_call_duration = api_call_end - api_call_start
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Update completed: Received updated itinerary{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ API Call duration: {api_call_duration:.2f} seconds{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Response length: {len(response_text)} characters{Colors.RESET}")
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Response content: {response_text}{Colors.RESET}")
            
            # Extract JSON from response (handle ```json code blocks)
            updated_json = extract_json_from_response(response_text)
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔧 Extracted JSON from update response{Colors.RESET}")
            
            # Try to validate updated JSON
            try:
                json.loads(updated_json)
                logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Updated response is valid JSON{Colors.RESET}")
            except json.JSONDecodeError as e:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Updated response is not valid JSON: {e}{Colors.RESET}")
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔍 Updated response raw text: {repr(updated_json)}{Colors.RESET}")
                # Return the extracted content anyway, it might still be useful
                
        except Exception as e:
            api_call_end = time.time()
            api_call_duration = api_call_end - api_call_start
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in update API call: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ Update API call failed after: {api_call_duration:.2f} seconds{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
            raise
        
        # Calculate total time and log summary
        end_time = time.time()
        total_duration = end_time - start_time
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}🎉 Itinerary update process completed successfully!{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 UPDATE TIMING SUMMARY{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}🔄 Update API call time: {api_call_duration:.2f}s{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}⏱️ Total update time: {total_duration:.2f}s{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}📈 API efficiency: {(api_call_duration/total_duration)*100:.1f}% (API time / total time){Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 60}{Colors.RESET}")
        
        # Extract destination from itinerary if not provided
        if not destination:
            try:
                itinerary_data = json.loads(updated_json)
                destination = itinerary_data.get('destination', '')
                if not destination:
                    # Try to extract from title or other fields
                    title = itinerary_data.get('title', '')
                    if title:
                        # Try to extract city name from title patterns like "3-Day Tokyo Itinerary"
                        import re
                        city_match = re.search(r'(?:Day\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Itinerary|Trip)', title)
                        if city_match:
                            destination = city_match.group(1)
                logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📍 Extracted destination for image search: {destination}{Colors.RESET}")
            except:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Could not extract destination from itinerary{Colors.RESET}")
        
        # Add images to updated activities
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🖼️ Adding images to updated activities...{Colors.RESET}")
        image_start_time = time.time()
        
        try:
            updated_json_with_images = add_images_to_activities(updated_json, destination=destination)
            image_end_time = time.time()
            image_duration = image_end_time - image_start_time
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Images added to updated activities{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}⏱️ Image processing duration: {image_duration:.2f} seconds{Colors.RESET}")
            
            # Update total duration to include image processing
            total_duration_with_images = total_duration + image_duration
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}⏱️ Total update time (with images): {total_duration_with_images:.2f}s{Colors.RESET}")
            
            return updated_json_with_images
            
        except Exception as e:
            image_end_time = time.time()
            image_duration = image_end_time - image_start_time
            
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error adding images to updated activities: {e}{Colors.RESET}")
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ Image processing failed after: {image_duration:.2f} seconds{Colors.RESET}")
            logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🔄 Returning updated itinerary without images{Colors.RESET}")
            
            return updated_json
        
    except Exception as e:
        # Calculate time even on error
        end_time = time.time()
        total_duration = end_time - start_time
        
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Critical error in update_itinerary function: {e}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error repr: {repr(e)}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}⏱️ Total execution time before error: {total_duration:.2f}s{Colors.RESET}")
        
        raise


def create_itinerary_with_test_case(test_case_index: int = 0, model: str = "gemini-2.5-pro") -> str:
    """
    Creates an itinerary using a test case from test_cases.py
    
    Args:
        test_case_index (int): Index of test case to use (0-9)
        model (str): Gemini model to use
        
    Returns:
        str: Final optimized itinerary in JSON format
    """
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.MAGENTA}🧪 Loading test case {test_case_index}{Colors.RESET}")
    
    try:
        from test_cases import get_test_case
        
        test_case = get_test_case(test_case_index)
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.MAGENTA}🧪 Test case loaded: {test_case}{Colors.RESET}")
        
        return create_itinerary(
            city_name=test_case["city_name"],
            user_pref=test_case["user_pref"],
            n_days=test_case["n_days"],
            model=model
        )
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in create_itinerary_with_test_case: {e}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error type: {type(e).__name__}{Colors.RESET}")
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}🔍 Error details: {str(e)}{Colors.RESET}")
        raise


def verify_image_url(image_url: str, timeout: int = 10) -> bool:
    """
    Verify if an image URL is accessible and returns a valid image.
    Less strict verification for better reliability.
    
    Args:
        image_url (str): URL of the image to verify
        timeout (int): Timeout in seconds for the request
        
    Returns:
        bool: True if image is accessible, False otherwise
    """
    try:
        # Use HEAD request to check if URL is accessible without downloading the full image
        response = requests.head(image_url, timeout=timeout, allow_redirects=True)
        
        # Accept a wider range of status codes (200, 301, 302, etc.)
        if response.status_code not in [200, 301, 302, 304]:
            # Try GET request if HEAD fails (some servers don't support HEAD)
            try:
                response = requests.get(image_url, timeout=timeout, stream=True, allow_redirects=True)
                if response.status_code not in [200, 301, 302, 304]:
                    return False
            except:
                return False
            
        # More lenient content type checking - accept if header exists and contains 'image'
        # or if no content-type header is present (some CDNs don't send it)
        content_type = response.headers.get('content-type', '').lower()
        if content_type and 'image' not in content_type and content_type != '':
            # Only reject if we're sure it's not an image
            if any(bad_type in content_type for bad_type in ['text/html', 'text/plain', 'application/json']):
                return False
            
        # More lenient size checking - only reject extremely small files (< 100 bytes)
        # or extremely large files (> 50MB)
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                # Only reject very small (< 100 bytes) or huge files (> 50MB)
                if size < 100 or size > 50 * 1024 * 1024:
                    return False
            except ValueError:
                pass  # Ignore invalid content-length headers
                
        return True
        
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False


def google_cse_image_search(query: str, api_key: str, cse_id: str, num_results: int = 5, verify_urls: bool = True, delay: float = 0.1, retry_count: int = 2) -> list:
    """
    Search for images using Google Custom Search API with retry logic.
    
    Args:
        query (str): Search query for images
        api_key (str): Google API key
        cse_id (str): Custom Search Engine ID
        num_results (int): Number of results to return (default: 5)
        verify_urls (bool): Whether to verify image URLs before returning (default: True)
        delay (float): Delay in seconds after API call to avoid rate limiting (default: 0.1)
        retry_count (int): Number of retries if API call fails (default: 2)
        
    Returns:
        list: List of verified image URLs
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "searchType": "image",
        "num": num_results,
        "safe": "active",  # Add safe search
        "imgSize": "medium",  # Prefer medium-sized images
        "imgType": "photo"  # Prefer photos over clipart
    }
    
    for attempt in range(retry_count + 1):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json()
            
            # Check for API errors
            if "error" in results:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Google CSE API error: {results['error']}{Colors.RESET}")
                if attempt < retry_count:
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
                    continue
                return []
            
            items = results.get("items", [])
            if not items:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ No image results for query: '{query}'{Colors.RESET}")
                return []
                
            image_urls = [item["link"] for item in items]
            
            if not verify_urls:
                # Add delay to avoid rate limiting
                if delay > 0:
                    time.sleep(delay)
                return image_urls
                
            # Verify each image URL with retries
            verified_urls = []
            for img_url in image_urls:
                if verify_image_url(img_url):
                    verified_urls.append(img_url)
                    logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✓ Verified image URL: {img_url[:50]}...{Colors.RESET}")
                else:
                    logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}✗ Failed to verify image URL: {img_url[:50]}...{Colors.RESET}")
            
            # Add delay to avoid rate limiting
            if delay > 0:
                time.sleep(delay)
            
            return verified_urls
            
        except requests.exceptions.RequestException as e:
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in Google CSE image search (attempt {attempt + 1}): {e}{Colors.RESET}")
            if attempt < retry_count:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
                continue
            return []
        except Exception as e:
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Unexpected error in image search (attempt {attempt + 1}): {e}{Colors.RESET}")
            if attempt < retry_count:
                time.sleep(delay * (attempt + 1))
                continue
            return []
    
    return []


def get_fallback_image_url(activity_name: str, activity_description: str = "") -> str:
    """
    Get a reliable fallback image URL based on activity type or keywords.
    Uses multiple fallback sources for better reliability.
    
    Args:
        activity_name (str): Name of the activity
        activity_description (str): Description of the activity
        
    Returns:
        str: Fallback image URL
    """
    # Convert to lowercase for keyword matching
    text = f"{activity_name} {activity_description}".lower()
    
    # Define multiple fallback images for better reliability (using Picsum for guaranteed availability)
    fallback_images = {
        # Food & Dining
        ('food', 'restaurant', 'lunch', 'dinner', 'breakfast', 'cafe', 'eat', 'sushi', 'pizza', 'cooking', 'meal'): [
            "https://picsum.photos/400/300?random=1",
            "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop",
            "https://source.unsplash.com/400x300/?food,restaurant"
        ],
        
        # Transportation  
        ('transport', 'travel', 'train', 'bus', 'flight', 'taxi', 'metro', 'subway', 'airport', 'station'): [
            "https://picsum.photos/400/300?random=2",
            "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=300&fit=crop",
            "https://source.unsplash.com/400x300/?transportation,travel"
        ],
        
        # Museums & Culture
        ('museum', 'gallery', 'art', 'culture', 'temple', 'church', 'historic', 'monument', 'architecture', 'heritage'): [
            "https://picsum.photos/400/300?random=3",
            "https://images.unsplash.com/photo-1534312527009-56c7b22b5bcd?w=400&h=300&fit=crop",
            "https://source.unsplash.com/400x300/?museum,art,culture"
        ],
        
        # Nature & Parks
        ('park', 'garden', 'nature', 'beach', 'mountain', 'lake', 'forest', 'sunset', 'sunrise', 'outdoor', 'landscape'): [
            "https://picsum.photos/400/300?random=4", 
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop",
            "https://source.unsplash.com/400x300/?nature,park,landscape"
        ],
        
        # Entertainment & Activities
        ('show', 'theater', 'concert', 'entertainment', 'shopping', 'market', 'activity', 'tour', 'performance'): [
            "https://picsum.photos/400/300?random=5",
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400&h=300&fit=crop", 
            "https://source.unsplash.com/400x300/?entertainment,activity"
        ],
        
        # Hotels & Accommodation
        ('hotel', 'accommodation', 'check-in', 'check-out', 'room', 'stay', 'lodge', 'hostel'): [
            "https://picsum.photos/400/300?random=6",
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop",
            "https://source.unsplash.com/400x300/?hotel,accommodation"
        ]
    }
    
    # Check for keyword matches and return first available fallback
    for keywords, image_urls in fallback_images.items():
        if any(keyword in text for keyword in keywords):
            for img_url in image_urls:
                if verify_image_url(img_url, timeout=5):
                    return img_url
            # If all fail, return the first one anyway
            return image_urls[0]
    
    # Default fallback images with multiple options
    default_fallbacks = [
        "https://picsum.photos/400/300?random=7",
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&h=300&fit=crop",
        "https://source.unsplash.com/400x300/?travel,tourism"
    ]
    
    for img_url in default_fallbacks:
        if verify_image_url(img_url, timeout=5):
            return img_url
    
    # Ultimate fallback - a reliable placeholder service
    return "https://via.placeholder.com/400x300/8B5CF6/FFFFFF?text=Travel+Activity"


def process_single_activity_image(activity: dict, api_key: str, cse_id: str, destination: str = "", use_fallback: bool = True) -> Tuple[dict, str]:
    """
    Process a single activity to add an image URL with guaranteed fallback.
    
    Args:
        activity (dict): Activity dictionary
        api_key (str): Google API key for Custom Search
        cse_id (str): Custom Search Engine ID
        destination (str): Destination/city name to include in search query
        use_fallback (bool): Whether to use fallback images
        
    Returns:
        Tuple[dict, str]: (updated_activity, result_status)
        result_status can be: 'verified', 'fallback', 'placeholder'
    """
    activity_name = activity.get('name', '')
    if not activity_name:
        # Even if no name, provide a generic fallback
        if use_fallback:
            activity['image'] = get_fallback_image_url("", "")
            return activity, 'fallback'
        return activity, 'failed'

    try:
        # Create search query with destination for more specific results
        search_query = f"{activity_name} {destination}".strip() if destination else activity_name
        
        logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Image search query: '{search_query}'{Colors.RESET}")
        
        # Search for image with verification and retry logic
        image_urls = google_cse_image_search(
            search_query, api_key, cse_id, 
            num_results=5,  # Get more results for better chances
            verify_urls=True, 
            delay=0.05,
            retry_count=1  # Quick retry for failed searches
        )
        
        if image_urls:
            activity['image'] = image_urls[0]  # Use the first verified image
            return activity, 'verified'
        
        # If no verified images found, try a simpler query without destination
        if destination:
            logging.debug(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Retrying with simpler query: '{activity_name}'{Colors.RESET}")
            image_urls = google_cse_image_search(
                activity_name, api_key, cse_id,
                num_results=3,
                verify_urls=True,
                delay=0.05,
                retry_count=1
            )
            
            if image_urls:
                activity['image'] = image_urls[0]
                return activity, 'verified'
        
        # If still no images, use fallback
        if use_fallback:
            activity_description = activity.get('description', '')
            fallback_context = f"{activity_name} {activity_description} {destination}".strip()
            fallback_url = get_fallback_image_url(activity_name, fallback_context)
            activity['image'] = fallback_url
            return activity, 'fallback'
        else:
            return activity, 'failed'
            
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error processing activity '{activity_name}': {e}{Colors.RESET}")
        
        # Always provide a fallback image even if there's an error
        if use_fallback:
            try:
                activity_description = activity.get('description', '')
                fallback_context = f"{activity_name} {activity_description} {destination}".strip()
                fallback_url = get_fallback_image_url(activity_name, fallback_context)
                activity['image'] = fallback_url
                return activity, 'fallback'
            except:
                # Ultimate fallback
                activity['image'] = "https://via.placeholder.com/400x300/8B5CF6/FFFFFF?text=Travel+Activity"
                return activity, 'placeholder'
        
        return activity, 'failed'


def add_images_to_activities(itinerary_json: str, destination: str = "", api_key: str = "AIzaSyA1Grg9lYjY2xa-ksP_d1VdSli3B_9LCLM", cse_id: str = "3788ce9cca864429b", use_fallback: bool = True, max_workers: int = 5) -> str:
    """
    Add image URLs to activities in the itinerary JSON using parallel processing.
    
    Args:
        itinerary_json (str): JSON string of the itinerary
        destination (str): Destination/city name to include in search queries for more specific results
        api_key (str): Google API key for Custom Search (if None, will use environment variable)
        cse_id (str): Custom Search Engine ID (if None, will use environment variable)
        use_fallback (bool): Whether to use fallback images when no verified image is found
        max_workers (int): Maximum number of parallel threads (default: 5)
        
    Returns:
        str: Updated itinerary JSON with image URLs
    """
    
    # Get API credentials from environment if not provided
    if api_key=="":
        api_key = os.getenv("GOOGLE_CSE_API_KEY")
    if cse_id=="":
        cse_id = os.getenv("GOOGLE_CSE_ID")
    
    # Validate required credentials
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}🔑 API Key: {api_key[:10]}...{Colors.RESET}")
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}🔍 CSE ID: {cse_id}{Colors.RESET}")
    if not api_key or not cse_id:
        logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Google Custom Search credentials not available. Skipping image processing.{Colors.RESET}")
        logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}   Please set GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID environment variables{Colors.RESET}")
        return itinerary_json
    
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🖼️ Starting parallel image processing for activities{Colors.RESET}")
    if destination:
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📍 Using destination in search queries: {destination}{Colors.RESET}")
    else:
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ No destination provided - using activity names only{Colors.RESET}")
    
    try:
        # Parse the JSON
        itinerary_data = json.loads(itinerary_json)
        
        if 'days' not in itinerary_data:
            logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ No 'days' key found in itinerary data{Colors.RESET}")
            return itinerary_json
        
        # Collect all activities with their positions for parallel processing
        activities_to_process = []
        total_activities = 0
        
        for day_index, day in enumerate(itinerary_data['days']):
            if 'activities' not in day:
                continue
                
            for activity_index, activity in enumerate(day['activities']):
                if isinstance(activity, dict) and 'name' in activity:
                    activities_to_process.append({
                        'activity': activity,
                        'day_index': day_index,
                        'activity_index': activity_index,
                        'day_num': day.get('day', day_index + 1)
                    })
                    total_activities += 1
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Found {total_activities} activities to process across {len(itinerary_data['days'])} days{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.MAGENTA}🚀 Using {max_workers} parallel workers{Colors.RESET}")
        
        # Process activities in parallel
        images_added = 0
        fallback_images_used = 0
        failed_searches = 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all activities for parallel processing
            future_to_activity = {
                executor.submit(process_single_activity_image, item['activity'], api_key, cse_id, destination, use_fallback): item
                for item in activities_to_process
            }
            
            # Process completed futures as they finish
            for future in as_completed(future_to_activity):
                item = future_to_activity[future]
                day_index = item['day_index']
                activity_index = item['activity_index']
                day_num = item['day_num']
                
                try:
                    updated_activity, result_status = future.result()
                    
                    # Update the activity in the original data structure
                    itinerary_data['days'][day_index]['activities'][activity_index] = updated_activity
                    
                    activity_name = updated_activity.get('name', 'Unknown')
                    
                    if result_status == 'verified':
                        images_added += 1
                        image_url = updated_activity.get('image', '')
                        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Day {day_num}: Added verified image for '{activity_name}': {image_url[:50]}...{Colors.RESET}")
                    elif result_status == 'fallback':
                        fallback_images_used += 1
                        image_url = updated_activity.get('image', '')
                        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}🔄 Day {day_num}: Used fallback image for '{activity_name}': {image_url[:50]}...{Colors.RESET}")
                    else:
                        failed_searches += 1
                        logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}⚠️ Day {day_num}: No image found for '{activity_name}'{Colors.RESET}")
                        
                except Exception as e:
                    failed_searches += 1
                    activity_name = item['activity'].get('name', 'Unknown')
                    logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Day {day_num}: Error processing '{activity_name}': {e}{Colors.RESET}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Log summary
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}🎉 Parallel image processing completed!{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Total processing time: {processing_time:.2f} seconds{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Average time per activity: {processing_time/total_activities:.2f} seconds{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Total activities processed: {total_activities}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}📊 Verified images added: {images_added}{Colors.RESET}")
        
        if fallback_images_used > 0:
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 Fallback images used: {fallback_images_used}{Colors.RESET}")
        
        if failed_searches > 0:
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📊 Failed searches (no image): {failed_searches}{Colors.RESET}")
        
        total_with_images = images_added + fallback_images_used
        success_rate = (total_with_images / total_activities * 100) if total_activities > 0 else 0
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}📊 Success rate: {success_rate:.1f}% ({total_with_images}/{total_activities} activities have images){Colors.RESET}")
        
        # Return updated JSON
        return json.dumps(itinerary_data, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error parsing itinerary JSON: {e}{Colors.RESET}")
        return itinerary_json
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error adding images to activities: {e}{Colors.RESET}")
        return itinerary_json


def diagnose_image_issues(itinerary_json: str) -> dict:
    """
    Diagnose image-related issues in an itinerary.
    
    Args:
        itinerary_json (str): JSON string of the itinerary
        
    Returns:
        dict: Diagnostic information about images
    """
    try:
        itinerary_data = json.loads(itinerary_json)
        
        diagnostics = {
            'total_activities': 0,
            'activities_with_images': 0,
            'activities_without_images': 0,
            'broken_image_urls': [],
            'working_image_urls': [],
            'activities_missing_images': [],
            'image_verification_results': {}
        }
        
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.CYAN}🔍 Starting image diagnostics...{Colors.RESET}")
        
        if 'days' not in itinerary_data:
            return diagnostics
        
        for day_index, day in enumerate(itinerary_data['days']):
            if 'activities' not in day:
                continue
                
            for activity_index, activity in enumerate(day['activities']):
                if isinstance(activity, dict) and 'name' in activity:
                    diagnostics['total_activities'] += 1
                    activity_name = activity.get('name', 'Unknown')
                    
                    if 'image' in activity and activity['image']:
                        diagnostics['activities_with_images'] += 1
                        image_url = activity['image']
                        
                        # Test if the image is accessible
                        is_working = verify_image_url(image_url, timeout=10)
                        diagnostics['image_verification_results'][activity_name] = {
                            'url': image_url,
                            'working': is_working,
                            'day': day.get('day', day_index + 1)
                        }
                        
                        if is_working:
                            diagnostics['working_image_urls'].append(image_url)
                        else:
                            diagnostics['broken_image_urls'].append({
                                'activity': activity_name,
                                'url': image_url,
                                'day': day.get('day', day_index + 1)
                            })
                    else:
                        diagnostics['activities_without_images'] += 1
                        diagnostics['activities_missing_images'].append({
                            'activity': activity_name,
                            'day': day.get('day', day_index + 1)
                        })
        
        # Calculate percentages
        total = diagnostics['total_activities']
        if total > 0:
            diagnostics['image_coverage_percentage'] = (diagnostics['activities_with_images'] / total) * 100
            diagnostics['working_image_percentage'] = (len(diagnostics['working_image_urls']) / total) * 100
        
        # Log results
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}📊 DIAGNOSTICS SUMMARY{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}{'=' * 50}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}Total activities: {diagnostics['total_activities']}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}Activities with images: {diagnostics['activities_with_images']}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}Activities without images: {diagnostics['activities_without_images']}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}Working images: {len(diagnostics['working_image_urls'])}{Colors.RESET}")
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.RED}Broken images: {len(diagnostics['broken_image_urls'])}{Colors.RESET}")
        
        if diagnostics.get('image_coverage_percentage'):
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}Image coverage: {diagnostics['image_coverage_percentage']:.1f}%{Colors.RESET}")
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.BLUE}Working image rate: {diagnostics['working_image_percentage']:.1f}%{Colors.RESET}")
        
        if diagnostics['activities_missing_images']:
            logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}Activities missing images:{Colors.RESET}")
            for item in diagnostics['activities_missing_images']:
                logging.warning(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}  - Day {item['day']}: {item['activity']}{Colors.RESET}")
        
        if diagnostics['broken_image_urls']:
            logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}Broken image URLs:{Colors.RESET}")
            for item in diagnostics['broken_image_urls']:
                logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}  - Day {item['day']}: {item['activity']} -> {item['url'][:50]}...{Colors.RESET}")
        
        return diagnostics
        
    except json.JSONDecodeError as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error parsing itinerary JSON: {e}{Colors.RESET}")
        return {'error': 'Invalid JSON format'}
    except Exception as e:
        logging.error(f"{Colors.ITINERARY_PREFIX} {Colors.RED}❌ Error in diagnostics: {e}{Colors.RESET}")
        return {'error': str(e)}


if __name__ == "__main__":
    # Set logging level to DEBUG for maximum detail
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Example usage with a test case
    print("Creating itinerary for Tokyo...")
    try:
        result = create_itinerary_with_test_case(0)  # Tokyo test case
        print("\nFinal Optimized Itinerary:")
        print(result)
    except Exception as e:
        logging.error(f"❌ Error creating itinerary: {e}")
        print(f"Error creating itinerary: {e}")
        
    # Example usage with custom parameters
    # result = create_itinerary(
    #     city_name="Paris",
    #     user_pref="art, museums, cafes, and romantic walks",
    #     n_days=4
    # )
    # print(result)
