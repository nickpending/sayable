import os
import logging
from typing import Dict, List, Tuple, Any
import anthropic
from datetime import datetime, timedelta
import time
import yaml

# Configure logger
logger = logging.getLogger(__name__)


class SayableError(Exception):
    """Base exception for Sayable-specific errors"""

    pass


class SayableAPIError(SayableError):
    """Raised when API calls fail"""

    pass


class SayableInputError(SayableError):
    """Raised for invalid input"""

    pass


class ConfigurationError(Exception):
    """Raised for invalid configuration file"""

    pass


def load_config(file_path):
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except (FileNotFoundError, yaml.YAMLError) as e:
        raise ConfigurationError(f"Error loading configuration file: {str(e)}")


class SayableAssistant:
    def __init__(
        self, model="claude-3-5-haiku-20241022", max_tokens=1000, config="config.yaml"
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.last_call = None
        self.min_interval = timedelta(milliseconds=100)

        try:
            config = load_config(config)
            self.system_prompt = config["sayable_system_prompt"]
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise SayableError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)
        except ConfigurationError as e:
            logger.error("Configuration file error.")
            raise
        except Exception as e:
            logger.error("Failed to initialize Sayable Assistant", exc_info=True)
            raise
        logger.debug("Initialized")

    def transform(self, text) -> str:
        """Transform input text into speech-friendly output"""
        if self.last_call and datetime.now() - self.last_call < self.min_interval:
            wait_time = self.min_interval.total_seconds()
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s before next API call")
            time.sleep(wait_time)
        self.last_call = datetime.now()

        if not text or not isinstance(text, str):
            raise SayableInputError("Input must be a non-empty string")
        messages = []
        try:
            messages.append({"role": "user", "content": text})
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages,
                system=self.system_prompt,
            )
            logger.debug(response)
            if not response.content:
                raise SayableAPIError("Received empty response from API")

            logger.debug(f"Received a response: {response.content}")
            return response.content[0]
        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                logger.error("Claude API is currently too busy to process requests")
                raise SayableAPIError(
                    "Service temporarily overloaded - please try again later"
                )
            else:
                logger.error(
                    f"API call failed with status {e.status_code}", exc_info=True
                )
                raise SayableAPIError(f"API call failed: {str(e)}")
        except Exception as e:
            logger.error("Failed to get response", exc_info=True)
            raise SayableError(f"Failed to get response: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        assistant = SayableAssistant()
        transformed_text = assistant.transform(
            "Based on the Censys data, the IP 130.35.229.127 is running both HTTP (port 80) and HTTPS (port 443) services"
        )
        transformed_text = assistant.transform(
            "The server is returning 404 responses on both ports, with standard security headers like Cache-Control and X-Content-Type-Options."
        )
    except SayableError as e:
        logger.error(f"Main execution failed: {e}")
