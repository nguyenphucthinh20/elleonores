import boto3
import json
from botocore.exceptions import ClientError
import re
import ast


class BedrockClient:
    """A client class for interacting with Amazon Bedrock."""
    
    def __init__(self, region="ap-northeast-1"):
        """Initialize the Bedrock Runtime client with the specified region.
        
        Args:
            region (str): AWS region name. Defaults to "ap-northeast-1".
        """
        self.region = region
        self.client = boto3.client("bedrock-runtime", region_name=region)
    
    def invoke_model(self, prompt, model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", max_tokens=4096):
        """Invoke Amazon Bedrock with a given prompt and return the response text.
        
        Args:
            prompt (str): The prompt to send to the model.
            model_id (str): The model ID to use. Defaults to Claude 3.5 Sonnet.
            max_tokens (int): Maximum number of tokens to generate. Defaults to 4096.
            
        Returns:
            str or None: The generated text if successful, None otherwise.
        """
        messages_API_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        body = json.dumps(messages_API_body)
        accept = "application/json"
        contentType = "application/json"

        try:
            response = self.client.invoke_model(
                modelId=model_id,
                body=body,
                contentType=contentType,
                accept=accept
            )

            response_body = json.loads(response["body"].read())
            generated_text = response_body["content"][0]["text"]            
            return generated_text

        except ClientError as e:
            print(f"ClientError: {e.response['Error']['Message']}")
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


bedrock = BedrockClient()
