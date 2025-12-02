# Text-to-Speech

indoxhub provides a unified interface for generating audio from text using text-to-speech models across various AI providers. This guide covers how to use the text-to-speech capabilities.

## Basic Usage

The simplest way to generate audio from text is with the `text_to_speech()` method:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

# Generate audio from text
response = client.text_to_speech(
    input="Hello, welcome to indoxhub!",
    model="openai/tts-1"
)

# Check if audio was generated successfully
if response["success"]:
    print("Audio generated successfully!")
    audio_url = response["data"]["url"]
    print(f"Audio URL: {audio_url}")
else:
    print(f"Error: {response['message']}")
```

## Model Selection

You can use different text-to-speech models from various providers:

```python
# OpenAI TTS-1 (faster, lower quality)
tts1_response = client.text_to_speech(
    input="This is generated with TTS-1",
    model="openai/tts-1"
)

# OpenAI TTS-1-HD (slower, higher quality)
tts1_hd_response = client.text_to_speech(
    input="This is generated with TTS-1-HD",
    model="openai/tts-1-hd"
)
```

## BYOK (Bring Your Own Key) Support

indoxhub supports BYOK for text-to-speech, allowing you to use your own API keys for AI providers:

```python
# Use your own OpenAI API key for TTS
response = client.text_to_speech(
    input="Hello, this is generated with my own OpenAI API key",
    model="openai/tts-1",
    voice="alloy",
    byok_api_key="sk-your-openai-key-here"
)

```

### BYOK Benefits for Text-to-Speech

- **No Credit Deduction**: Your indoxhub credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific TTS features
- **Higher Quality**: Use provider's native text-to-speech capabilities

## Voice Selection

Different providers offer different voices. For OpenAI, you can choose from several voices:

```python
# Available OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

for voice in voices:
    response = client.text_to_speech(
        input=f"This is the {voice} voice.",
        model="openai/tts-1",
        voice=voice
    )
    print(f"Generated audio with {voice} voice")
```

### Voice Characteristics

- **alloy**: Balanced, neutral voice
- **echo**: Clear, professional voice
- **fable**: Warm, storytelling voice
- **onyx**: Deep, authoritative voice
- **nova**: Bright, energetic voice
- **shimmer**: Soft, gentle voice

## Audio Format Options

You can specify different audio output formats:

```python
# MP3 format (default)
mp3_response = client.text_to_speech(
    input="This will be in MP3 format",
    model="openai/tts-1",
    response_format="mp3"
)

# Opus format (good for real-time applications)
opus_response = client.text_to_speech(
    input="This will be in Opus format",
    model="openai/tts-1",
    response_format="opus"
)

# AAC format (good for mobile devices)
aac_response = client.text_to_speech(
    input="This will be in AAC format",
    model="openai/tts-1",
    response_format="aac"
)

# FLAC format (lossless quality)
flac_response = client.text_to_speech(
    input="This will be in FLAC format",
    model="openai/tts-1",
    response_format="flac"
)
```

## Speed Control

Adjust the playback speed of the generated audio:

```python
# Slower speech (0.25x speed)
slow_response = client.text_to_speech(
    input="This will be spoken very slowly.",
    model="openai/tts-1",
    speed=0.25
)

# Normal speed (1.0x - default)
normal_response = client.text_to_speech(
    input="This will be spoken at normal speed.",
    model="openai/tts-1",
    speed=1.0
)

# Faster speech (2.0x speed)
fast_response = client.text_to_speech(
    input="This will be spoken quickly.",
    model="openai/tts-1",
    speed=2.0
)

# Maximum speed (4.0x speed)
max_speed_response = client.text_to_speech(
    input="This will be spoken very quickly.",
    model="openai/tts-1",
    speed=4.0
)
```

!!! note "Speed Range"
The speed parameter accepts values from 0.25 to 4.0, where:

    - 0.25 = Quarter speed (very slow)
    - 1.0 = Normal speed
    - 4.0 = Quadruple speed (very fast)

## Advanced Usage

### With Instructions

Some providers may support additional instructions for fine-tuning the speech generation:

```python
response = client.text_to_speech(
    input="Welcome to our premium service!",
    model="openai/tts-1",
    voice="nova",
    instructions="Speak with enthusiasm and excitement"
)
```

### Complete Example

Here's a comprehensive example that demonstrates all the parameters:

```python
from indoxhub import Client

client = Client(api_key="your_api_key")

def generate_speech_sample():
    response = client.text_to_speech(
        input="Welcome to indoxhub, your unified AI API gateway. "
               "We provide seamless access to multiple AI providers "
               "through a single, consistent interface.",
        model="openai/tts-1-hd",
        voice="alloy",
        response_format="mp3",
        speed=1.1,
        instructions="Speak clearly and professionally"
    )

    if response["success"]:
        print(f"✅ Audio generated successfully!")
        print(f"📊 Usage: {response.get('usage', {})}")
        print(f"🏗️ Provider: {response.get('provider', 'N/A')}")
        print(f"🤖 Model: {response.get('model', 'N/A')}")
        print(f"⏱️ Duration: {response.get('duration_ms', 0)}ms")

        # The audio URL is available in response["data"]["url"]
        audio_url = response["data"]["url"]
        print(f"🔗 Audio URL: {audio_url}")

        # You can download the audio file using the URL
        # import requests
        # audio_response = requests.get(audio_url)
        # with open("generated_speech.mp3", "wb") as f:
        #     f.write(audio_response.content)

        return audio_url
    else:
        print(f"❌ Error: {response.get('message', 'Unknown error')}")
        return None

# Generate the speech
audio_data = generate_speech_sample()
```

## Response Format

The text-to-speech response includes several fields:

```python
{
    "request_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00.000Z",
    "duration_ms": 1250,
    "provider": "openai",
    "model": "tts-1",
    "success": true,
    "message": "Audio generated successfully",
    "data": {
        "url": "https://generated-audio.example.com/audio_12345.mp3"
    },
    "usage": {
        "characters": 150,
        "cost": 0.0075
    },
    "raw_response": {...}
}
```

### Response Fields

- **request_id**: Unique identifier for the request
- **created_at**: Timestamp when the audio was generated
- **duration_ms**: Time taken to generate the audio in milliseconds
- **provider**: AI provider used (e.g., "openai")
- **model**: Specific model used (e.g., "tts-1")
- **success**: Boolean indicating if the generation was successful
- **message**: Human-readable status message
- **data**: Object containing the URL to the generated audio file
- **usage**: Usage statistics including character count and cost
- **raw_response**: Raw response from the provider

## Error Handling

Handle common errors that may occur during text-to-speech generation:

```python
from indoxhub.exceptions import (
    ModelNotAvailableError,
    InsufficientCreditsError,
    ValidationError
)

try:
    response = client.text_to_speech(
        input="Text to convert to speech",
        model="openai/tts-1",
        voice="alloy"
    )

    if response["success"]:
        audio_url = response["data"]["url"]
        # Process the audio URL
    else:
        print(f"Generation failed: {response['message']}")

except ModelNotAvailableError as e:
    print(f"Model is not available: {e}")
except InsufficientCreditsError as e:
    print(f"Insufficient credits: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### Text Optimization

- **Keep it concise**: Shorter texts generally produce better audio quality
- **Use punctuation**: Proper punctuation helps with natural speech rhythm
- **Avoid special characters**: Some symbols may not be pronounced correctly

```python
# Good example
good_text = "Hello! Welcome to our service. How can we help you today?"

# Less optimal example
poor_text = "hello welcome 2 our service how can we help u 2day???"

response = client.text_to_speech(
    input=good_text,
    model="openai/tts-1",
    voice="alloy"
)
```

### Voice Selection Guidelines

- **Presentations**: Use "echo" or "onyx" for professional content
- **Storytelling**: Use "fable" for narrative content
- **Casual content**: Use "alloy" or "nova" for friendly interactions
- **Customer service**: Use "shimmer" for gentle, helpful responses

### Performance Considerations

- **Use TTS-1** for real-time applications where speed is important
- **Use TTS-1-HD** for high-quality content where audio fidelity matters
- **Cache generated audio** when possible to avoid repeated API calls
- **Monitor usage costs** as TTS can be more expensive than text generation

## Provider-Specific Features

### OpenAI Features

OpenAI's TTS models support:

- Multiple high-quality voices optimized for different use cases
- Variable speed control from 0.25x to 4.0x
- Multiple output formats (MP3, Opus, AAC, FLAC)
- Consistent quality across different text lengths

### Future Provider Support

indoxhub is designed to support multiple TTS providers. As new providers are added, they may offer:

- Different voice options and characteristics
- Unique audio processing capabilities
- Provider-specific parameters and optimizations
- Various pricing models and usage limits

## Troubleshooting

### Common Issues

**Audio not generating:**

- Check that your API key has TTS permissions
- Verify you have sufficient credits
- Ensure the model name is correct

**Poor audio quality:**

- Try using TTS-1-HD instead of TTS-1
- Adjust the speed parameter
- Use proper punctuation in your text

**Unsupported parameters:**

- Some parameters may not be supported by all providers
- Check provider documentation for supported features
- Use `additional_params` for provider-specific options

### Getting Help

If you encounter issues:

1. Check the error message in the response
2. Verify your API key and credits
3. Review the parameter documentation
4. Contact support with your request ID for specific issues

!!! tip "Rate Limits"
Text-to-speech requests may have different rate limits than text generation. Monitor your usage and implement appropriate retry logic for production applications.

_Last updated: Nov 16, 2025_