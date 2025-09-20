"""
Example script demonstrating speech-to-text functionality in IndoxRouter.

This script shows how to use the new speech-to-text capabilities added to the IndoxRouter client.
"""

from indoxrouter import Client


def main():
    # Initialize the client with your API key
    client = Client(api_key="your_api_key_here")

    try:
        print("=== IndoxRouter Speech-to-Text Examples ===\n")

        # Example 1: Basic transcription with file path
        print("1. Transcribing audio file:")
        try:
            response = client.speech_to_text(
                "path/to/your/audio.mp3", model="openai/whisper-1"
            )
            if response["success"]:
                print(f"   Transcription: {response['text']}")
            else:
                print(f"   Error: {response['message']}")
        except Exception as e:
            print(f"   Example 1 Error: {e}")

        print()

        # Example 2: Transcription with specific language and format
        print("2. Transcription with language specification:")
        try:
            response = client.speech_to_text(
                "path/to/your/audio.wav",
                model="openai/whisper-1",
                language="en",
                response_format="verbose_json",
                temperature=0.2,
            )
            if response["success"]:
                print(f"   Transcription: {response['text']}")
                if "language" in response:
                    print(f"   Detected Language: {response['language']}")
            else:
                print(f"   Error: {response['message']}")
        except Exception as e:
            print(f"   Example 2 Error: {e}")

        print()

        # Example 3: Transcription with timestamps
        print("3. Transcription with detailed timestamps:")
        try:
            response = client.speech_to_text(
                "path/to/your/audio.mp3",
                model="openai/whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
            )
            if response["success"]:
                print(f"   Transcription: {response['text']}")
                if "segments" in response:
                    print(f"   Number of segments: {len(response['segments'])}")
            else:
                print(f"   Error: {response['message']}")
        except Exception as e:
            print(f"   Example 3 Error: {e}")

        print()

        # Example 4: Audio translation to English
        print("4. Translating foreign audio to English:")
        try:
            response = client.translate_audio(
                "path/to/your/foreign_audio.mp3",
                model="openai/whisper-1",
                response_format="text",
            )
            if response["success"]:
                print(f"   Translation: {response['text']}")
            else:
                print(f"   Error: {response['message']}")
        except Exception as e:
            print(f"   Example 4 Error: {e}")

        print()

        # Example 5: Using audio data bytes instead of file path
        print("5. Transcription using audio bytes:")
        try:
            # Read audio file as bytes
            with open("path/to/your/audio.mp3", "rb") as f:
                audio_data = f.read()

            response = client.speech_to_text(
                audio_data,
                model="openai/whisper-1",
                filename="my_audio.mp3",  # Optional filename hint
            )
            if response["success"]:
                print(f"   Transcription: {response['text']}")
            else:
                print(f"   Error: {response['message']}")
        except FileNotFoundError:
            print(
                "   Example 5 Note: Audio file not found - this is expected for the example"
            )
        except Exception as e:
            print(f"   Example 5 Error: {e}")

        print()

        # Example 6: Using BYOK (Bring Your Own Key)
        print("6. Using BYOK (Bring Your Own Key):")
        try:
            response = client.speech_to_text(
                "path/to/your/audio.mp3",
                model="openai/whisper-1",
                byok_api_key="sk-your-openai-key-here",
            )
            if response["success"]:
                print(f"   Transcription: {response['text']}")
                print(
                    "   Note: This used your own OpenAI API key (no IndoxRouter credits used)"
                )
            else:
                print(f"   Error: {response['message']}")
        except Exception as e:
            print(f"   Example 6 Error: {e}")

        print("\n=== Examples completed ===")

    finally:
        # Clean up the client
        client.close()


if __name__ == "__main__":
    main()
