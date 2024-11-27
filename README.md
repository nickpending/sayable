# Sayable

Make technical text speakable! Sayable is a Python package that transforms technical text into a format that's friendly for text-to-speech systems, powered by Claude AI.

## Features

- Transforms technical jargon into speech-friendly text
- Handles URLs, IP addresses, and technical notation
- Expands abbreviations and acronyms
- Smart formatting for numbers and special characters
- Rate limiting for API efficiency
- Configurable system prompts

## Installation

```bash
pip install sayable
```

For development:
```bash
git clone [repository-url]
cd sayable
pip install -r requirements.txt
```

## Quick Start

```python
from sayable import SayableAssistant

# Initialize the assistant
assistant = SayableAssistant()

# Transform technical text
text = "The server at 192.168.1.1:8080 returned a 404 error"
speakable = assistant.transform(text)
print(speakable)
# Output: "The server at IP address one nine two dot one six eight..."
```

## Configuration

1. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key'
```

2. (Optional) Create a `config.yaml` file to customize the system prompt:
```yaml
sayable_system_prompt: |
  Your custom system prompt here
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
isort .
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Error Handling

Sayable includes several custom exception classes:
- `SayableError`: Base exception class
- `SayableAPIError`: API-related errors
- `SayableInputError`: Invalid input errors
- `ConfigurationError`: Configuration issues

## License

MIT License - see LICENSE file for details