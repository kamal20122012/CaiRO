import os
import logging
import json
import re
import time
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
    logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}🎯 Step 0/4: Selecting best matching persona...{Colors.RESET}")
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
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 1/4: Formatted first prompt for attractions categorization{Colors.RESET}")
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
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 1/4 completed: Received attractions categorization{Colors.RESET}")
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
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 2/4: Formatted second prompt for initial itinerary creation (using {selected_persona_key}){Colors.RESET}")
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
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 2/4 completed: Received initial itinerary{Colors.RESET}")
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
        logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.YELLOW}📝 Step 3/4: Added third prompt for location-based optimization{Colors.RESET}")
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
            
            logging.info(f"{Colors.ITINERARY_PREFIX} {Colors.GREEN}✅ Step 3/4 completed: Received final optimized itinerary{Colors.RESET}")
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


def update_itinerary(itinerary_json: str, user_query: str, model: str = "gemini-2.5-pro") -> str:
    """
    Updates an existing itinerary based on user query using Gemini API.
    
    Args:
        itinerary_json (str): The complete itinerary JSON to be updated
        user_query (str): User's request for changes to the itinerary
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
