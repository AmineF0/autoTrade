import requests
from typing import List, Optional
import time
from datetime import datetime

class APIKeyRotator:
    def __init__(self, api_keys: List[str], base_url: str):
        """
        Initialize the API key rotator with a list of API keys and base URL.
        
        Args:
            api_keys (List[str]): List of API keys to rotate through
            base_url (str): Base URL for the API
        """
        self.api_keys = api_keys
        self.base_url = base_url
        self.current_key_index = 0
        self.failed_keys = set()
        self.last_request_time = 0
        self.rate_limit_wait = 12  # Wait time in seconds between requests

    def get_next_valid_key(self) -> Optional[str]:
        """Get the next valid API key from the rotation."""
        attempts = 0
        while attempts < len(self.api_keys):
            if self.current_key_index >= len(self.api_keys):
                self.current_key_index = 0
            
            current_key = self.api_keys[self.current_key_index]
            if current_key not in self.failed_keys:
                return current_key
            
            self.current_key_index += 1
            attempts += 1
        
        return None

    def make_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """
        Make an API request with automatic key rotation on failure.
        
        Args:
            endpoint (str): API endpoint to call
            params (dict): Query parameters for the request
            
        Returns:
            Optional[dict]: JSON response if successful, None if all keys failed
        """
        # Respect rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_wait:
            time.sleep(self.rate_limit_wait - time_since_last_request)

        while True:
            api_key = self.get_next_valid_key()
            if api_key is None:
                print("All API keys have failed or expired")
                return None

            try:
                params['apikey'] = api_key
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                # Check for API-specific error responses
                data = response.json()
                if "Error Message" in data or "Note" in data:
                    raise Exception(f"API Error: {data.get('Error Message') or data.get('Note')}")
                
                self.last_request_time = time.time()
                return data

            except Exception as e:
                print(f"Error with API key {api_key}: {str(e)}")
                self.failed_keys.add(api_key)
                self.current_key_index += 1