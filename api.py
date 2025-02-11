import google.auth
from google.auth.transport.requests import Request
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_access_token():
    """Get OAuth token for API authentication"""
    credentials, _ = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

def generate_caption(prompt: str) -> str:
    """
    Generate caption using Vertex AI endpoint
    """
    try:
        logger.debug(f"Attempting to generate caption for prompt: {prompt}")
        
        # Use the exact endpoint URL that works in test_print.py
        endpoint_url = "https://7462099544692490240.asia-southeast1-275499389350.prediction.vertexai.goog/v1/projects/groovy-legacy-438407-u5/locations/asia-southeast1/endpoints/7462099544692490240:predict"
        
        # Set up headers with OAuth token
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }
        
        # Use the exact data format that works in test_print.py
        data = {
            "instances": [{
                "inputs": f"### Instruction:\nGenerate a girlfriend caption\n\n### Input:\n{prompt}\n\n### Response:\n"
            }]
        }
        
        logger.debug(f"Making request with data: {data}")
        response = requests.post(endpoint_url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_json = response.json()
            logger.debug(f"Received response: {response_json}")
            # Extract the actual caption from the response
            predictions = response_json.get('predictions', [])
            if predictions and len(predictions) > 0:
                return predictions[0]
        else:
            logger.error(f"Error status code: {response.status_code}")
            logger.error(f"Error response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating caption: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return None 