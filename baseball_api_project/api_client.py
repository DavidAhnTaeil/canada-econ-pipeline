"""API Client for API-Sports Baseball"""

import os
from dotenv import load_dotenv
import requests

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_SPORTS_KEY")

BASE_URL = "https://v1.baseball.api-sports.io"


def make_request(endpoint: str, params: dict = None) -> dict:
    """Send a request to the API with authentication.
    
    This is THE pattern for any authenticated API:
    1. Set your API key in the headers
    2. Send the request
    3. Parse the JSON response
    
    
    Args:
        endpoint: API endpoint (e.g., '/teams')
        params: Query parameters to filter results.
        
    Returns:
        The JSON response as a dictionary
        
    """
    headers = {
        "x-apisports-key": API_KEY
    }

    url = BASE_URL + endpoint
    print(f"Calling API: {url}")

    response = requests.get(url, headers = headers, params = params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # API-Sports wraps all responses in this structure
    print(f"Results: {data['results']} items returned")
    
    return data