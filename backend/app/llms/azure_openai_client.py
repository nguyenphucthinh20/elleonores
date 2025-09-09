import os
import json
from openai import AzureOpenAI
from openai import OpenAIError
import re
import ast
from app.core.config import settings


class AzureOpenAIClient:
    """A client class for interacting with Azure OpenAI."""
    
    def __init__(self, api_key=None, api_base=None, api_version=None, model="gpt-4o"):
        """Initialize the Azure OpenAI client with the specified configuration.
        
        Args:
            api_key (str): Azure OpenAI API key. If None, uses environment variable.
            api_base (str): Azure OpenAI endpoint. If None, uses environment variable.
            api_version (str): API version. If None, uses environment variable or default.
            model (str): The deployment model name. Defaults to "gpt-4o".
        """
        self.api_key = api_key or settings.AZURE_OPENAI_KEY
        self.api_base = api_base or settings.AZURE_OPENAI_ENDPOINT
        self.api_version = api_version or settings.API_VERSION
        self.model = model
        
        # Validate required parameters
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required")
        if not self.api_base:
            raise ValueError("Azure OpenAI endpoint is required")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            base_url=f"{self.api_base}/openai/deployments/{self.model}",
        )
    
    def invoke_model(self, prompt, system_message="You are a helpful assistant.", 
                     max_tokens=2000, temperature=0.7):
        """Invoke Azure OpenAI with a given prompt and return the response text.
        
        Args:
            prompt (str): The prompt to send to the model.
            system_message (str): System message to set model behavior.
            max_tokens (int): Maximum number of tokens to generate. Defaults to 2000.
            temperature (float): Temperature for response generation. Defaults to 0.7.
            
        Returns:
            str or None: The generated text if successful, None otherwise.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                        ],
                    },
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Extract the generated text from response
            generated_text = response.choices[0].message.content
            return generated_text

        except OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
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


azure_client = AzureOpenAIClient()
