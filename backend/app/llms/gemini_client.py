import os
import json
from google import genai
import re
import ast
from app.core.config import settings


class GeminiClient:
    """A client class for interacting with Gemini."""
    
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model

        if not self.api_key:
            raise ValueError("Gemini API key is required")
        self.client = genai.Client()
    
    def invoke_model(self, prompt, max_tokens=2000, temperature=0.7):
        """Invoke Azure OpenAI with a given prompt and return the response text.
        
        Args:
            prompt (str): The prompt to send to the model.
            max_tokens (int): Maximum number of tokens to generate. Defaults to 2000.
            temperature (float): Temperature for response generation. Defaults to 0.7.
            
        Returns:
            str or None: The generated text if successful, None otherwise.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            generated_text = response.text
            return generated_text

        except Exception as e:
            print(f"Gemini API Error: {e}")
            return None

    @staticmethod
    def parse_json_string(entry):
        """Parse a JSON string from a raw model response.

        Args:
            entry (str or tuple): The raw model response.

        Returns:
            dict: Parsed JSON object.

        Raises:
            ValueError: If no JSON block is found or parsing fails.
        """
        if isinstance(entry, tuple):
            entry = entry[0]
        
        if "```json" in entry:
            match = re.search(r"```json\s*(\{.*?\})\s*```", entry, re.DOTALL)
            if match:
                json_block = match.group(1)
                cleaned = json_block.replace('""', '"')
                return json.loads(cleaned)
            else:
                raise ValueError("No JSON block found in text containing markdown.")
        
        try:
            cleaned = ast.literal_eval(f"'''{entry}'''")
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Error parsing JSON: {e}")


gemini_client = GeminiClient()
