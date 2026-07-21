import os
import re
import time
import json
import logging
from dotenv import load_dotenv
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GroqClientWrapper:
    """Wrapper around the Groq API client with rate limiting, retries, and schema validation."""

    def __init__(self, api_key=None, rate_limit_interval=2.4, max_retries=3):
        """
        api_key: Groq API Key. If None, loaded from env GROQ_API_KEY.
        rate_limit_interval: Minimum time (in seconds) between requests to stay under 30 rpm.
        max_retries: Number of retries for failures before giving up.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY environment variable not found. Requests will fail unless configured.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

        self.rate_limit_interval = rate_limit_interval
        self.max_retries = max_retries
        self.last_request_time = 0.0

        # Model bindings
        self.bulk_model = "llama-3.1-8b-instant"
        self.quality_model = "llama-3.3-70b-versatile"

    def _wait_for_rate_limit(self):
        """Enforces rate limit by sleeping if the last request was too recent."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.rate_limit_interval:
            sleep_time = self.rate_limit_interval - elapsed
            logger.debug(f"Rate limiting active. Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _clean_json_response(self, response_text):
        """Tries to extract JSON text from markdown formatting or other garbage wraps."""
        text = response_text.strip()
        # Find markdown code block boundaries first
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no markdown blocks, find the first '{' and last '}'
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx + 1].strip()
            
        return text

    def request_json(self, system_prompt, user_prompt, model=None, response_schema=None):
        """
        Sends a request to Groq, enforces JSON mode/response, cleans output, and parses to dict.
        """
        if not self.client:
            raise ValueError("Groq client not initialized. Please set GROQ_API_KEY environment variable.")

        model = model or self.bulk_model
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self._wait_for_rate_limit()
                
                logger.info(f"Sending Groq request (Attempt {attempt}/{self.max_retries}) using model: {model}")
                
                # Groq support JSON mode via response_format parameter
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model,
                    temperature=0.0,  # Deterministic responses
                    response_format={"type": "json_object"}
                )
                
                raw_response = chat_completion.choices[0].message.content
                cleaned_response = self._clean_json_response(raw_response)
                
                # Parse to dict
                data = json.loads(cleaned_response)
                
                # Optional basic schema validation
                if response_schema:
                    for key, val_type in response_schema.items():
                        if key not in data:
                            raise KeyError(f"Expected key '{key}' not found in LLM response.")
                        # Check type (simplified check)
                        if val_type and not isinstance(data[key], val_type):
                            raise TypeError(f"Key '{key}' expected type {val_type}, got {type(data[key])}")
                
                return data

            except json.JSONDecodeError as jde:
                logger.error(f"JSON decode failed on attempt {attempt}: {jde}. Raw content:\n{raw_response}")
                if attempt == self.max_retries:
                    raise jde
            except Exception as e:
                logger.error(f"Error on attempt {attempt}: {e}")
                
                # If we get a rate limit error (429), back off longer
                if hasattr(e, 'status_code') and e.status_code == 429:
                    backoff = attempt * 5.0
                    logger.warning(f"Rate limited by Groq API. Backing off for {backoff} seconds...")
                    time.sleep(backoff)
                
                if attempt == self.max_retries:
                    raise e
                    
            # Incremental standard delay between retries
            time.sleep(attempt * 1.5)

        raise RuntimeError("Failed to complete Groq API call after all retries.")

# Global instance
client = GroqClientWrapper()
