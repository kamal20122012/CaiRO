import os
import logging
import json
import re
import time
from google.genai import types
from prompt_lib import itnr_1, itnr_2, itnr_3
from llm_utils import get_conversation_response_gemini, add_user_message_to_conversation

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
    
    logging.info(f"🚀 Starting itinerary creation for {city_name} ({n_days} days)")
    logging.info(f"📋 User preferences: {user_pref}")
    logging.info(f"🤖 Using model: {model}")
    
    try:
        # Format the first prompt with city name
        prompt_1 = itnr_1.format(city_name=city_name)
        logging.info("📝 Step 1/3: Formatted first prompt for attractions categorization")
        logging.debug(f"🔍 Prompt 1 content: {prompt_1}")
        
        # Start conversation with first prompt
        logging.info("🔄 Adding first prompt to conversation history...")
        conversation_history = add_user_message_to_conversation([], prompt_1)
        logging.debug(f"🔍 Conversation history length after adding prompt 1: {len(conversation_history)}")
        
        # Generate response for first prompt (attractions categorization)
        logging.info("🔄 Making API call 1/3: Getting attractions categorization...")
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
            
            logging.info("✅ Step 1/3 completed: Received attractions categorization")
            logging.info(f"⏱️ API Call 1 duration: {api_call_1_duration:.2f} seconds")
            logging.info(f"📊 Response 1 length: {len(response_1_text)} characters")
            logging.debug(f"🔍 Response 1 content: {response_1_text}")
            logging.debug(f"🔍 Conversation history length after response 1: {len(conversation_history)}")
                
        except Exception as e:
            api_call_1_end = time.time()
            api_call_1_duration = api_call_1_end - api_call_1_start
            api_call_times.append(("API Call 1 (Failed)", api_call_1_duration))
            
            logging.error(f"❌ Error in API call 1/3: {e}")
            logging.error(f"⏱️ API Call 1 failed after: {api_call_1_duration:.2f} seconds")
            logging.error(f"🔍 Error type: {type(e).__name__}")
            logging.error(f"🔍 Error details: {str(e)}")
            raise
        
        # Format and add second prompt with user preferences and number of days
        prompt_2 = itnr_2.format(user_pref=user_pref, n_days=n_days)
        logging.info("📝 Step 2/3: Formatted second prompt for initial itinerary creation")
        logging.debug(f"🔍 Prompt 2 content: {prompt_2}")
        
        logging.info("🔄 Adding second prompt to conversation history...")
        conversation_history = add_user_message_to_conversation(conversation_history, prompt_2)
        logging.debug(f"🔍 Conversation history length after adding prompt 2: {len(conversation_history)}")
        
        # Generate response for second prompt (initial itinerary)
        logging.info("🔄 Making API call 2/3: Creating initial itinerary...")
        api_call_2_start = time.time()
        try:
            response_2_text, conversation_history = get_conversation_response_gemini(
                model="gemini-2.5-flash",
                conversation_history=conversation_history,
                grounding=False  # No grounding needed for itinerary creation
            )
            api_call_2_end = time.time()
            api_call_2_duration = api_call_2_end - api_call_2_start
            api_call_times.append(("API Call 2 (Initial itinerary)", api_call_2_duration))
            
            logging.info("✅ Step 2/3 completed: Received initial itinerary")
            logging.info(f"⏱️ API Call 2 duration: {api_call_2_duration:.2f} seconds")
            logging.info(f"📊 Response 2 length: {len(response_2_text)} characters")
            logging.debug(f"🔍 Response 2 content: {response_2_text}")
            logging.debug(f"🔍 Conversation history length after response 2: {len(conversation_history)}")
                
        except Exception as e:
            api_call_2_end = time.time()
            api_call_2_duration = api_call_2_end - api_call_2_start
            api_call_times.append(("API Call 2 (Failed)", api_call_2_duration))
            
            logging.error(f"❌ Error in API call 2/3: {e}")
            logging.error(f"⏱️ API Call 2 failed after: {api_call_2_duration:.2f} seconds")
            logging.error(f"🔍 Error type: {type(e).__name__}")
            logging.error(f"🔍 Error details: {str(e)}")
            raise
        
        # Add third prompt for optimization
        logging.info("📝 Step 3/3: Added third prompt for location-based optimization")
        logging.debug(f"🔍 Prompt 3 content: {itnr_3}")
        
        logging.info("🔄 Adding third prompt to conversation history...")
        conversation_history = add_user_message_to_conversation(conversation_history, itnr_3)
        logging.debug(f"🔍 Conversation history length after adding prompt 3: {len(conversation_history)}")
        
        # Generate final optimized response
        logging.info("🔄 Making API call 3/3: Optimizing itinerary based on locations...")
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
            
            logging.info("✅ Step 3/3 completed: Received final optimized itinerary")
            logging.info(f"⏱️ API Call 3 duration: {api_call_3_duration:.2f} seconds")
            logging.info(f"📊 Response 3 length: {len(response_3_text)} characters")
            logging.debug(f"🔍 Response 3 content: {response_3_text}")
            logging.debug(f"🔍 Final conversation history length: {len(conversation_history)}")
            
            # Extract JSON from final response (handle ```json code blocks)
            final_json = extract_json_from_response(response_3_text)
            logging.info("🔧 Extracted JSON from final response")
            
            # Try to validate final JSON
            try:
                json.loads(final_json)
                logging.info("✅ Final response is valid JSON")
            except json.JSONDecodeError as e:
                logging.warning(f"⚠️ Final response is not valid JSON: {e}")
                logging.warning(f"🔍 Final response raw text: {repr(final_json)}")
                # Return the extracted content anyway, it might still be useful
                
        except Exception as e:
            api_call_3_end = time.time()
            api_call_3_duration = api_call_3_end - api_call_3_start
            api_call_times.append(("API Call 3 (Failed)", api_call_3_duration))
            
            logging.error(f"❌ Error in API call 3/3: {e}")
            logging.error(f"⏱️ API Call 3 failed after: {api_call_3_duration:.2f} seconds")
            logging.error(f"🔍 Error type: {type(e).__name__}")
            logging.error(f"🔍 Error details: {str(e)}")
            raise
        
        # Calculate total time and log summary
        end_time = time.time()
        total_duration = end_time - start_time
        total_api_time = sum(duration for _, duration in api_call_times)
        
        logging.info("🎉 Itinerary creation process completed successfully!")
        logging.info("=" * 60)
        logging.info("📊 TIMING SUMMARY")
        logging.info("=" * 60)
        
        for call_name, duration in api_call_times:
            percentage = (duration / total_api_time) * 100 if total_api_time > 0 else 0
            logging.info(f"⏱️ {call_name}: {duration:.2f}s ({percentage:.1f}%)")
        
        logging.info("-" * 60)
        logging.info(f"🔄 Total API call time: {total_api_time:.2f}s")
        logging.info(f"⏱️ Total execution time: {total_duration:.2f}s")
        logging.info(f"📈 API efficiency: {(total_api_time/total_duration)*100:.1f}% (API time / total time)")
        logging.info("=" * 60)
        
        return final_json
        
    except Exception as e:
        # Calculate time even on error
        end_time = time.time()
        total_duration = end_time - start_time
        total_api_time = sum(duration for _, duration in api_call_times)
        
        logging.error(f"❌ Critical error in create_itinerary function: {e}")
        logging.error(f"🔍 Error type: {type(e).__name__}")
        logging.error(f"🔍 Error details: {str(e)}")
        logging.error(f"🔍 Error repr: {repr(e)}")
        
        # Log timing summary even on error
        if api_call_times:
            logging.error("=" * 60)
            logging.error("📊 TIMING SUMMARY (FAILED EXECUTION)")
            logging.error("=" * 60)
            
            for call_name, duration in api_call_times:
                percentage = (duration / total_api_time) * 100 if total_api_time > 0 else 0
                logging.error(f"⏱️ {call_name}: {duration:.2f}s ({percentage:.1f}%)")
            
            logging.error("-" * 60)
            logging.error(f"🔄 Total API call time: {total_api_time:.2f}s")
            logging.error(f"⏱️ Total execution time: {total_duration:.2f}s")
            logging.error("=" * 60)
        
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
    logging.info(f"🧪 Loading test case {test_case_index}")
    
    try:
        from test_cases import get_test_case
        
        test_case = get_test_case(test_case_index)
        logging.info(f"🧪 Test case loaded: {test_case}")
        
        return create_itinerary(
            city_name=test_case["city_name"],
            user_pref=test_case["user_pref"],
            n_days=test_case["n_days"],
            model=model
        )
    except Exception as e:
        logging.error(f"❌ Error in create_itinerary_with_test_case: {e}")
        logging.error(f"🔍 Error type: {type(e).__name__}")
        logging.error(f"🔍 Error details: {str(e)}")
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
