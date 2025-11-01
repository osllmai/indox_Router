"""
Video Generation Examples using IndoxRouter Client

This script demonstrates how to use the IndoxRouter Python client to generate
videos using Google's Veo models.

Requirements:
    pip install indoxrouter

Set your API key as an environment variable:
    export INDOX_ROUTER_API_KEY="your-api-key-here"

Or pass it directly to the Client constructor.
"""

from indoxrouter import Client
import os


def example_basic_text_to_video():
    """Example 1: Basic text-to-video generation"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Text-to-Video")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A neon hologram of a cat driving at top speed",
        model="google/veo-3.0-generate-001",
        aspect_ratio="16:9",
        resolution="720p",
        duration=8,
    )

    print(f"Success: {response['success']}")
    print(f"Model: {response['model']}")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")

    client.close()


def example_video_with_audio():
    """Example 2: Generate video with synchronized audio"""
    print("\n" + "=" * 60)
    print("Example 2: Video with Audio")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A butterfly lands on a flower, audio cue: gentle nature sounds",
        model="google/veo-3.0-generate-001",
        duration=6,
        resolution="720p",
        generate_audio=True,  # Enable audio generation
    )

    print(f"Success: {response['success']}")
    print(f"Model: {response['model']}")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")
    print("Note: Video includes synchronized audio!")

    client.close()


def example_high_resolution():
    """Example 3: Generate high resolution (1080p) video"""
    print("\n" + "=" * 60)
    print("Example 3: High Resolution (1080p)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A futuristic city at sunset with flying cars",
        model="google/veo-3.0-generate-001",
        aspect_ratio="16:9",
        resolution="1080p",  # High resolution
        duration=4,
    )

    print(f"Success: {response['success']}")
    print(f"Resolution: 1080p")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")

    client.close()


def example_fast_generation():
    """Example 4: Fast video generation using Veo 3 Fast"""
    print("\n" + "=" * 60)
    print("Example 4: Fast Video Generation")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="Waves crashing on a beach",
        model="google/veo-3.0-fast-generate-001",  # Fast model
        duration=8,
        resolution="720p",
    )

    print(f"Success: {response['success']}")
    print(f"Model: Veo 3 Fast (cheaper and faster)")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")

    client.close()


def example_portrait_mode():
    """Example 5: Portrait mode video (9:16 aspect ratio)"""
    print("\n" + "=" * 60)
    print("Example 5: Portrait Mode Video")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A vertical video of a waterfall flowing down",
        model="google/veo-3.0-generate-001",
        aspect_ratio="9:16",  # Portrait mode
        resolution="720p",
        duration=6,
    )

    print(f"Success: {response['success']}")
    print(f"Aspect Ratio: 9:16 (Portrait)")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")

    client.close()


def example_veo_31_advanced():
    """Example 6: Advanced Veo 3.1 with negative prompt"""
    print("\n" + "=" * 60)
    print("Example 6: Veo 3.1 with Negative Prompt")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A beautiful garden with colorful flowers",
        model="google/veo-3.1-generate-preview",
        duration=8,
        negative_prompt="rain, storm, dark clouds",  # What NOT to include
        person_generation="allow_adult",  # Control people generation
        resolution="720p",
    )

    print(f"Success: {response['success']}")
    print(f"Model: Veo 3.1 (Advanced features)")
    print(f"Negative Prompt: rain, storm, dark clouds")
    print(f"Cost: ${response['usage']['cost']:.4f}")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")

    client.close()


def example_multiple_videos():
    """Example 7: Generate multiple videos at once"""
    print("\n" + "=" * 60)
    print("Example 7: Generate Multiple Videos")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    response = client.videos(
        prompt="A scenic mountain landscape",
        model="google/veo-3.0-generate-001",
        duration=4,
        resolution="720p",
        n=2,  # Generate 2 videos
    )

    print(f"Success: {response['success']}")
    print(f"Videos generated: {len(response['data'])}")
    print(f"Total cost: ${response['usage']['cost']:.4f}")

    for i, video in enumerate(response["data"], 1):
        print(f"Video {i} URL: {video['url'][:80]}...")

    client.close()


def example_with_context_manager():
    """Example 8: Using context manager (recommended)"""
    print("\n" + "=" * 60)
    print("Example 8: Using Context Manager")
    print("=" * 60)

    with Client(api_key=os.getenv("INDOX_ROUTER_API_KEY")) as client:
        response = client.videos(
            prompt="A peaceful sunset over the ocean",
            model="google/veo-3.0-generate-001",
            duration=6,
            resolution="720p",
        )

        print(f"Success: {response['success']}")
        print(f"Cost: ${response['usage']['cost']:.4f}")
        print(f"Video URL: {response['data'][0]['url'][:80]}...")

    # Client automatically closed


def example_byok():
    """Example 9: Using your own Google API key (BYOK)"""
    print("\n" + "=" * 60)
    print("Example 9: BYOK (Bring Your Own Key)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Use your own Google API key - no credit deduction!
    response = client.videos(
        prompt="A time-lapse of clouds moving across the sky",
        model="google/veo-3.0-generate-001",
        duration=6,
        resolution="720p",
        byok_api_key=os.getenv("GOOGLE_API_KEY"),  # Your Google API key
    )

    print(f"Success: {response['success']}")
    print(f"Cost: $0.00 (using your own API key)")
    print(f"Video URL: {response['data'][0]['url'][:80]}...")
    print("Note: You pay Google directly at their rates!")

    client.close()


def example_error_handling():
    """Example 10: Proper error handling"""
    print("\n" + "=" * 60)
    print("Example 10: Error Handling")
    print("=" * 60)

    from indoxrouter import (
        InsufficientCreditsError,
        InvalidParametersError,
        ModelNotAvailableError,
    )

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    try:
        response = client.videos(
            prompt="Test video",
            model="google/veo-3.0-generate-001",
            duration=20,  # Invalid - max is 8 seconds
            resolution="720p",
        )
        print(f"Success: {response['success']}")

    except InvalidParametersError as e:
        print(f"❌ Invalid parameters: {str(e)}")
    except InsufficientCreditsError as e:
        print(f"❌ Not enough credits: {str(e)}")
    except ModelNotAvailableError as e:
        print(f"❌ Model not available: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()


# Model comparison information
def print_model_comparison():
    """Print comparison of available Veo models"""
    print("\n" + "=" * 60)
    print("VEO MODELS COMPARISON")
    print("=" * 60)

    models = [
        {
            "name": "veo-2.0-generate-001",
            "description": "Veo 2 (Stable)",
            "price": "$0.50/sec",
            "resolution": "720p",
            "duration": "5-8s",
            "audio": "No",
            "features": "Basic text-to-video",
        },
        {
            "name": "veo-3.0-generate-001",
            "description": "Veo 3 (Latest)",
            "price": "$0.20/sec (video), $0.40/sec (with audio)",
            "resolution": "720p, 1080p",
            "duration": "4-8s",
            "audio": "Optional",
            "features": "High quality + optional audio",
        },
        {
            "name": "veo-3.0-fast-generate-001",
            "description": "Veo 3 Fast",
            "price": "$0.15/sec (includes audio)",
            "resolution": "720p, 1080p",
            "duration": "4-8s",
            "audio": "Always included",
            "features": "Faster, cheaper, with audio",
        },
        {
            "name": "veo-3.1-generate-preview",
            "description": "Veo 3.1 (Advanced)",
            "price": "$0.40/sec (includes audio)",
            "resolution": "720p, 1080p",
            "duration": "4-8s",
            "audio": "Always included",
            "features": "Reference images, negative prompts",
        },
        {
            "name": "veo-3.1-fast-generate-preview",
            "description": "Veo 3.1 Fast",
            "price": "$0.15/sec (includes audio)",
            "resolution": "720p, 1080p",
            "duration": "4-8s",
            "audio": "Always included",
            "features": "Faster, with some advanced features",
        },
    ]

    for model in models:
        print(f"\n{model['description']} (google/{model['name']})")
        print(f"  Price: {model['price']}")
        print(f"  Resolution: {model['resolution']}")
        print(f"  Duration: {model['duration']}")
        print(f"  Audio: {model['audio']}")
        print(f"  Features: {model['features']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("INDOXROUTER VIDEO GENERATION EXAMPLES")
    print("=" * 60)

    # Print model comparison
    print_model_comparison()

    # Check if API key is set
    if not os.getenv("INDOX_ROUTER_API_KEY"):
        print("\n⚠️  Please set INDOX_ROUTER_API_KEY environment variable")
        print("   export INDOX_ROUTER_API_KEY='your-api-key-here'")
        return

    # Run examples
    examples = [
        ("Basic Text-to-Video", example_basic_text_to_video),
        ("Video with Audio", example_video_with_audio),
        ("High Resolution", example_high_resolution),
        ("Fast Generation", example_fast_generation),
        ("Portrait Mode", example_portrait_mode),
        ("Veo 3.1 Advanced", example_veo_31_advanced),
        ("Multiple Videos", example_multiple_videos),
        ("Context Manager", example_with_context_manager),
        ("Error Handling", example_error_handling),
    ]

    print("\n" + "=" * 60)
    print("Choose an example to run:")
    print("=" * 60)
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")
    print("=" * 60)

    try:
        choice = input("\nEnter your choice (0-9): ").strip()

        if choice == "0":
            for name, func in examples:
                try:
                    func()
                    print("\n✅ Example completed successfully")
                except Exception as e:
                    print(f"\n❌ Example failed: {str(e)}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            _, func = examples[int(choice) - 1]
            func()
            print("\n✅ Example completed successfully")
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
