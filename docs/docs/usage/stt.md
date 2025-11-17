# Speech-to-Text

IndoxRouter provides a unified interface for transcribing audio to text using speech-to-text models across various AI providers. This guide covers how to use the speech-to-text capabilities.

## Basic Usage

The simplest way to transcribe audio to text is with the `speech_to_text()` method:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

# Transcribe audio from file path
response = client.speech_to_text("path/to/audio.mp3")

# Check if transcription was successful
if response["success"]:
    print("Transcription:", response["text"])
else:
    print(f"Error: {response['message']}")
```

## File Input Options

You can provide audio in two ways:

### File Path

```python
# Using a file path
response = client.speech_to_text("path/to/audio.mp3")
```

### Audio Bytes

```python
# Using audio data as bytes
with open("audio.mp3", "rb") as f:
    audio_data = f.read()

response = client.speech_to_text(audio_data)
```

## Model Selection

You can use different speech-to-text models from various providers:

```python
# OpenAI Whisper-1 (default)
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1"
)

# Other providers (when available)
response = client.speech_to_text(
    "audio.mp3",
    model="provider/model-name"
)
```

## Language Specification

Specify the language of the audio for better accuracy:

```python
# English audio
response = client.speech_to_text(
    "english_audio.mp3",
    model="openai/whisper-1",
    language="en"
)

# Spanish audio
response = client.speech_to_text(
    "spanish_audio.mp3",
    model="openai/whisper-1",
    language="es"
)

# French audio
response = client.speech_to_text(
    "french_audio.mp3",
    model="openai/whisper-1",
    language="fr"
)
```

## Response Formats

Choose different output formats for your transcription:

```python
# JSON format (default) - returns structured data
json_response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="json"
)

# Plain text format - returns just the text
text_response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="text"
)

# SRT subtitle format
srt_response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="srt"
)

# Verbose JSON - includes detailed timing and metadata
verbose_response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="verbose_json"
)

# VTT subtitle format
vtt_response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="vtt"
)
```

## Timestamps and Segmentation

Get detailed timing information with timestamp granularities:

```python
# Get word-level timestamps
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word"]
)

# Get segment-level timestamps
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["segment"]
)

# Get both word and segment timestamps
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"]
)
```

## Temperature Control

Adjust the randomness/consistency of the transcription:

```python
# More consistent transcription (lower temperature)
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    temperature=0.0
)

# More creative transcription (higher temperature)
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    temperature=0.7
)
```

## Prompt Guidance

Use prompts to guide the transcription style:

```python
# Formal style prompt
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    prompt="This is a formal business meeting transcript."
)

# Technical content prompt
response = client.speech_to_text(
    "technical_audio.mp3",
    model="openai/whisper-1",
    prompt="This audio contains technical programming terms and code discussions."
)
```

## Audio Translation

Translate foreign language audio directly to English:

```python
# Translate Spanish audio to English
response = client.translate_audio(
    "spanish_audio.mp3",
    model="openai/whisper-1"
)

# Translate with specific format
response = client.translate_audio(
    "french_audio.mp3",
    model="openai/whisper-1",
    response_format="text"
)
```

## Using BYOK (Bring Your Own Key)

Use your own provider API keys:

```python
# Use your own OpenAI API key
response = client.speech_to_text(
    "audio.mp3",
    model="openai/whisper-1",
    byok_api_key="sk-your-openai-key-here"
)

# Translation with BYOK
response = client.translate_audio(
    "audio.mp3",
    model="openai/whisper-1",
    byok_api_key="sk-your-openai-key-here"
)
```

## Supported Audio Formats

The speech-to-text API supports various audio formats:

- **MP3** - Most common compressed format
- **WAV** - Uncompressed format (good quality)
- **FLAC** - Lossless compression
- **M4A** - Apple audio format
- **OGG** - Open-source compressed format
- **WEBM** - Web-optimized format

```python
# Examples with different formats
mp3_response = client.speech_to_text("audio.mp3")
wav_response = client.speech_to_text("audio.wav")
flac_response = client.speech_to_text("audio.flac")
```

## Response Format

The speech-to-text response includes several fields:

```python
{
    "request_id": "uuid-string",
    "created_at": "2024-01-15T10:30:00.000Z",
    "duration_ms": 2500,
    "provider": "openai",
    "model": "whisper-1",
    "success": true,
    "message": "Audio transcribed successfully",
    "text": "Hello, this is the transcribed text.",
    "language": "en",
    "usage": {
        "duration_seconds": 45.2,
        "cost": 0.0068
    },
    "raw_response": {...}
}
```

### Response Fields

- **request_id**: Unique identifier for the request
- **created_at**: Timestamp when the transcription was created
- **duration_ms**: Time taken to process the audio in milliseconds
- **provider**: AI provider used (e.g., "openai")
- **model**: Specific model used (e.g., "whisper-1")
- **success**: Boolean indicating if the transcription was successful
- **message**: Human-readable status message
- **text**: The transcribed text
- **language**: Detected or specified language
- **usage**: Usage statistics including duration and cost
- **raw_response**: Raw response from the provider

## Error Handling

Handle common errors that may occur during transcription:

```python
from indoxrouter.exceptions import (
    ModelNotAvailableError,
    InsufficientCreditsError,
    ValidationError,
    InvalidParametersError
)

try:
    response = client.speech_to_text(
        "audio.mp3",
        model="openai/whisper-1"
    )

    if response["success"]:
        text = response["text"]
        # Process the transcribed text
    else:
        print(f"Transcription failed: {response['message']}")

except ModelNotAvailableError as e:
    print(f"Model is not available: {e}")
except InsufficientCreditsError as e:
    print(f"Insufficient credits: {e}")
except InvalidParametersError as e:
    print(f"Invalid parameters: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### Audio Quality

- Use high-quality audio files for better transcription accuracy
- Minimize background noise when possible
- Ensure clear speech and appropriate volume levels

### File Size

- Keep audio files under 25MB for optimal processing
- For longer audio, consider splitting into smaller segments

### Language Specification

- Always specify the language when known for better accuracy
- Use the correct ISO language code (e.g., "en", "es", "fr")

### Response Format Selection

- Use "json" for most applications requiring structured data
- Use "text" when you only need the transcribed text
- Use "verbose_json" when you need detailed timing information
- Use "srt" or "vtt" for subtitle generation

### Cost Optimization

- Use appropriate temperature settings (lower values are more consistent)
- Consider using BYOK for high-volume transcriptions
- Monitor usage through the usage endpoint

## Complete Example

Here's a comprehensive example that demonstrates various features:

```python
from indoxrouter import Client

def transcribe_audio_file(file_path, language=None):
    client = Client(api_key="your_api_key")

    try:
        # Transcribe with detailed options
        response = client.speech_to_text(
            file_path,
            model="openai/whisper-1",
            language=language,
            response_format="verbose_json",
            temperature=0.2,
            timestamp_granularities=["word", "segment"]
        )

        if response["success"]:
            print(f"✅ Transcription successful!")
            print(f"📝 Text: {response['text']}")
            print(f"🌍 Language: {response.get('language', 'Unknown')}")
            print(f"⏱️  Duration: {response['usage']['duration_seconds']} seconds")
            print(f"💰 Cost: ${response['usage']['cost']}")

            # Process segments if available
            if "segments" in response:
                print(f"📊 Segments: {len(response['segments'])}")
                for i, segment in enumerate(response['segments'][:3]):  # First 3 segments
                    start = segment.get('start', 0)
                    end = segment.get('end', 0)
                    text = segment.get('text', '')
                    print(f"   {i+1}. [{start:.1f}s - {end:.1f}s]: {text}")

            return response['text']
        else:
            print(f"❌ Error: {response.get('message', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"💥 Exception: {e}")
        return None
    finally:
        client.close()

# Usage
transcribed_text = transcribe_audio_file("meeting_recording.mp3", language="en")
```

_Last updated: Nov 16, 2025_