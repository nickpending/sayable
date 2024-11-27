import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime, timedelta
from sayable import (
    SayableAssistant,
    SayableError,
    SayableAPIError,
    SayableInputError,
    ConfigurationError,
    load_config,
)


class TestSayableAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            "sayable_system_prompt": "Test system prompt"  # This matches what's in the code
        }
        self.config_path = "test_config.yaml"
        # Store original env var if it exists
        self.original_api_key = os.environ.get("ANTHROPIC_API_KEY")

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Restore original env var state
        if self.original_api_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.original_api_key
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)

    @patch("anthropic.Anthropic")
    @patch("sayable.sayable.load_config")  # Updated to patch the correct path
    def test_initialization(self, mock_load_config, mock_anthropic):
        # Setup
        mock_load_config.return_value = self.test_config
        os.environ["ANTHROPIC_API_KEY"] = "test_key"

        # Test successful initialization
        assistant = SayableAssistant()
        self.assertEqual(assistant.system_prompt, "Test system prompt")
        self.assertEqual(assistant.model, "claude-3-5-haiku-20241022")

        # Test missing API key
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with self.assertRaises(SayableError):
            SayableAssistant()

    @patch("anthropic.Anthropic")
    @patch("sayable.sayable.load_config")  # Updated to patch the correct path
    def test_transform_valid_input(self, mock_load_config, mock_anthropic):
        # Setup
        mock_load_config.return_value = self.test_config
        os.environ["ANTHROPIC_API_KEY"] = "test_key"
        mock_response = MagicMock()
        mock_response.content = ["transformed text"]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        assistant = SayableAssistant()
        result = assistant.transform("test input")
        self.assertEqual(result, "transformed text")

    @patch("anthropic.Anthropic")
    @patch("sayable.sayable.load_config")  # Updated to patch the correct path
    def test_transform_invalid_input(self, mock_load_config, mock_anthropic):
        # Setup
        mock_load_config.return_value = self.test_config
        os.environ["ANTHROPIC_API_KEY"] = "test_key"

        assistant = SayableAssistant()

        # Test empty string
        with self.assertRaises(SayableInputError):
            assistant.transform("")

        # Test None input
        with self.assertRaises(SayableInputError):
            assistant.transform(None)

    @patch("anthropic.Anthropic")
    @patch("sayable.sayable.load_config")  # Updated to patch the correct path
    def test_rate_limiting(self, mock_load_config, mock_anthropic):
        # Setup
        mock_load_config.return_value = self.test_config
        os.environ["ANTHROPIC_API_KEY"] = "test_key"
        mock_response = MagicMock()
        mock_response.content = ["transformed text"]
        mock_anthropic.return_value.messages.create.return_value = mock_response

        assistant = SayableAssistant()

        # First call
        start_time = datetime.now()
        assistant.transform("test input")

        # Second immediate call
        assistant.transform("test input")
        end_time = datetime.now()

        # Verify minimum interval was respected
        self.assertGreaterEqual(end_time - start_time, assistant.min_interval)

    def test_load_config(self):
        # Test invalid file path
        with self.assertRaises(ConfigurationError):
            load_config("nonexistent_file.yaml")


if __name__ == "__main__":
    unittest.main()
