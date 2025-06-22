import os
from typing import List
from google.genai import types
from llm_utils import get_conversation_response_gemini
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


def suggest_activities(city: str) -> List[str]:
    """
    Generates activity suggestions for a given city using the Gemini model.

    This function takes a city name, sends a formatted prompt to the Gemini API
    using the helper function from llm_utils, and processes the semicolon-separated
    response into a list of activity strings.

    Args:
        city: The name of the city for which to generate suggestions.

    Returns:
        A list of strings, where each string is a suggested activity.
        Returns an empty list if an error occurs.
    """
    try:
        # The prompt is structured as a multi-part message.
        # The first part provides the instructions and desired format.
        # The second part provides the input city.
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"""given the city as {city} give me 6-7 suggestions.the suggestions should be phrases or 1 words like - Hiking, Solo Traveling, Art Galleries etc... depending on the city, and the vibe of the trip. Keep the suggestions a little diverse too, dont cram things which are alike.
Strictly adhere to the format, no extra text
OUTPUT FORMAT:
sug1;sug2;sug3;sug4;sug5;

"""
                    )
                ],
            ),
        ]

        # Using "gemini-2.0-flash" with grounding enabled.
        # No thinking config needed.
        response_text, _ = get_conversation_response_gemini(
            model="gemini-2.5-flash",
            conversation_history=contents,
            grounding=True,
            thinking_budget=None,
        )

        if not response_text:
            logging.warning("Received an empty response from the model.")
            return []

        # The model is prompted to return suggestions separated by semicolons.
        suggestions = [
            suggestion.strip() for suggestion in response_text.split(";") if suggestion.strip()
        ]
        return suggestions

    except Exception as e:
        logging.error(f"An error occurred while suggesting activities for {city}: {e}")
        return []


if __name__ == "__main__":
    # This block allows for direct testing of the suggest_activities function.
    # It requires the GEMINI_API_KEY to be set in the environment.
    if "GEMINI_API_KEY" not in os.environ:
        print("Please set the GEMINI_API_KEY environment variable to run this test.")
    else:
        target_city = input("Enter a city to get activity suggestions for: ")
        if target_city:
            activity_suggestions = suggest_activities(target_city)
            print(activity_suggestions)
        else:
            print(f"Could not retrieve suggestions for {target_city}.")
