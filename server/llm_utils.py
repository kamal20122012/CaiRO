from google import genai
from google.genai import types
import os
import logging
from typing import List, Optional

def get_response_gemini(model: str, user_query: str, grounding: bool = True, thinking_budget: int = None) -> str:
    """
    Generate a response using Google's Gemini model with optional grounding and thinking control.
    
    Args:
        model (str): The Gemini model to use (e.g., "gemini-2.5-flash")
        user_query (str): The user's question or prompt
        grounding (bool): Whether to enable Google Search grounding (default: True)
        thinking_budget (int): Thinking budget for 2.5 models. 
                              None (default) = no thinking config,
                              0 = turn off thinking,
                              -1 = dynamic thinking,
                              positive int = thinking with budget
    
    Returns:
        str: The generated response text
    """
    # Configure the client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Configure generation settings based on grounding preference and thinking budget
    config_kwargs = {}
    
    # Add grounding tools if enabled
    if grounding:
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config_kwargs['tools'] = [grounding_tool]
    
    # Add thinking config if specified (for 2.5 models)
    if thinking_budget is not None:
        config_kwargs['thinking_config'] = types.ThinkingConfig(thinking_budget=thinking_budget)
    
    config = types.GenerateContentConfig(**config_kwargs)
    
    # Make the request
    response = client.models.generate_content(
        model=model,
        contents=user_query,
        config=config,
    )
    
    # Return the response text
    return response.text


def get_conversation_response_gemini(
    model: str, 
    conversation_history: List[types.Content], 
    grounding: bool = False, 
    thinking_budget: Optional[int] = None
) -> tuple[str, List[types.Content]]:
    """
    Generate a response using conversation history and return both response and updated history.
    
    Args:
        model (str): The Gemini model to use (e.g., "gemini-2.0-flash")
        conversation_history (List[types.Content]): List of conversation contents
        grounding (bool): Whether to enable Google Search grounding (default: False)
        thinking_budget (int): Thinking budget for 2.5 models
        
    Returns:
        tuple: (response_text, updated_conversation_history)
    """
    logging.debug(f"🔧 get_conversation_response_gemini called with model: {model}")
    logging.debug(f"🔧 Conversation history length: {len(conversation_history)}")
    logging.debug(f"🔧 Grounding enabled: {grounding}")
    logging.debug(f"🔧 Thinking budget: {thinking_budget}")
    
    try:
        # Configure the client
        logging.debug("🔧 Configuring Gemini client...")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Configure generation settings
        config_kwargs = {}
        
        # Add grounding tools if enabled
        if grounding:
            logging.debug("🔧 Adding grounding tool...")
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            config_kwargs['tools'] = [grounding_tool]
        
        # Add thinking config if specified
        if thinking_budget is not None:
            logging.debug(f"🔧 Adding thinking config with budget: {thinking_budget}")
            config_kwargs['thinking_config'] = types.ThinkingConfig(thinking_budget=thinking_budget)
        
        logging.debug(f"🔧 Config kwargs: {list(config_kwargs.keys())}")
        config = types.GenerateContentConfig(**config_kwargs)
        
        # Make the request with conversation history
        logging.debug("🔧 Making API request to Gemini...")
        response = client.models.generate_content(
            model=model,
            contents=conversation_history,
            config=config,
        )
        
        logging.debug(f"🔧 API response received")
        logging.debug(f"🔧 Response type: {type(response)}")
        
        # Check if response has text attribute
        if not hasattr(response, 'text'):
            logging.error(f"🔧 Response object doesn't have 'text' attribute")
            logging.error(f"🔧 Response attributes: {dir(response)}")
            raise AttributeError("Response object doesn't have 'text' attribute")
        
        # Get response text
        logging.debug("🔧 Extracting response text...")
        response_text = response.text
        logging.debug(f"🔧 Response text type: {type(response_text)}")
        logging.debug(f"🔧 Response text length: {len(response_text) if response_text else 'None'}")
        
        if response_text is None:
            logging.error("🔧 Response text is None!")
            raise ValueError("Response text is None")
        
        # Add the model's response to conversation history
        logging.debug("🔧 Adding model response to conversation history...")
        updated_history = conversation_history.copy()
        updated_history.append(
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text=response_text),
                ],
            )
        )
        
        logging.debug(f"🔧 Updated conversation history length: {len(updated_history)}")
        logging.debug("🔧 get_conversation_response_gemini completed successfully")
        
        return response_text, updated_history
        
    except Exception as e:
        logging.error(f"🔧 Error in get_conversation_response_gemini: {e}")
        logging.error(f"🔧 Error type: {type(e).__name__}")
        logging.error(f"🔧 Error details: {str(e)}")
        logging.error(f"🔧 Error repr: {repr(e)}")
        raise


def add_user_message_to_conversation(conversation_history: List[types.Content], message: str) -> List[types.Content]:
    """
    Add a user message to the conversation history.
    
    Args:
        conversation_history (List[types.Content]): Current conversation history
        message (str): User message to add
        
    Returns:
        List[types.Content]: Updated conversation history
    """
    logging.debug(f"🔧 Adding user message to conversation (length: {len(message)})")
    logging.debug(f"🔧 Current conversation history length: {len(conversation_history)}")
    
    try:
        updated_history = conversation_history.copy()
        updated_history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=message),
                ],
            )
        )
        logging.debug(f"🔧 Updated conversation history length: {len(updated_history)}")
        return updated_history
    except Exception as e:
        logging.error(f"🔧 Error in add_user_message_to_conversation: {e}")
        logging.error(f"🔧 Error type: {type(e).__name__}")
        logging.error(f"🔧 Error details: {str(e)}")
        raise




if __name__ == "__main__":
    # Get user input
    user_query = input("Enter your question: ")
    
    # Ask for grounding preference
    grounding_input = input("Enable grounding? (y/n): ").lower().strip()
    grounding = grounding_input in ['y', 'yes']
    
    # Ask for thinking budget (for 2.5 models)
    thinking_input = input("Thinking budget (press enter for none, 0 to turn off, -1 for dynamic, or positive number): ").strip()
    thinking_budget = None
    if thinking_input:
        try:
            thinking_budget = int(thinking_input)
        except ValueError:
            print("Invalid thinking budget, using default (none)")
    
    # Generate response
    try:
        response = get_response_gemini(
            model="gemini-2.5-pro",
            user_query=user_query,
            grounding=grounding,
            thinking_budget=thinking_budget
        )
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error generating response: {e}")
