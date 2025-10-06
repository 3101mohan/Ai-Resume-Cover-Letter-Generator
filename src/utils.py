# src/utils.py
# Gemini API call + text generation using the official Google GenAI SDK

from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, MODEL_NAME


def generate_text_with_gemini(prompt_text: str, max_output_tokens: int, temperature: float = 0.0, response_json_schema: dict = None) -> str:
    """
    Calls the Gemini API with a given prompt and returns the generated text.
    If response_json_schema is provided, the model returns a strict JSON object.
    """
    if not GEMINI_API_KEY:
        # In a real application, this should handle key loading/error, but for Canvas, 
        # we rely on the key being present.
        raise RuntimeError("⚠️ GEMINI_API_KEY not found. Please check your .env file.")

    try:
        # Initialize the client with the API Key
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Configuration for the generation
        config = types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
        
        # Set response format to JSON if a schema is provided
        if response_json_schema:
            config.response_mime_type = "application/json"
            config.response_schema = response_json_schema
        

        # Call the API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt_text,
            config=config,
        )

        # Process and return the text (either JSON string or plain text)
        if response.text:
            return response.text.strip()
        else:
            # Check for failure reasons like safety filters
            if response.candidates and response.candidates[0].finish_reason.name in ["SAFETY", "RECITATION"]:
                 return "⚠️ No text generated. Output blocked due to safety settings or policy violation."
            return "⚠️ No text generated. The model returned an empty response."

    except Exception as e:
        # Catch network errors, authentication failures, etc.
        raise RuntimeError(f"Gemini API Call Error: {type(e).__name__}: {e}")
