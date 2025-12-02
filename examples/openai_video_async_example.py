"""
OpenAI Async Video Generation Examples

This script demonstrates how to use indoxhub's async video generation
with OpenAI's Sora models.

OpenAI video generation is ASYNCHRONOUS - the request returns immediately
with a job_id, and you poll for completion.

Requirements:
    pip install indoxhub

Set your API key:
    export INDOX_ROUTER_API_KEY="your-api-key-here"
"""

from indoxhub import Client
import os
import time


def example_basic_async_video():
    """Example 1: Basic async video generation"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Async Video (OpenAI Sora)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation (returns immediately)
    response = client.videos(
        prompt="a person running from a police officer in soccer field",
        model="openai/sora-2",
        duration=4,
    )

    print(f"Success: {response['success']}")
    print(f"Message: {response['message']}")

    # Check if it's async
    if isinstance(response["data"], dict) and response["data"].get("is_async"):
        job_id = response["data"]["job_id"]
        status = response["data"]["status"]

        print(f"\n✓ Async job created!")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {status}")
        print(f"  Provider Video ID: {response['data']['provider_video_id']}")

        # Manual polling
        print("\nPolling for completion...")
        while True:
            job_status = client.get_video_job_status(job_id)
            print(
                f"  Status: {job_status['status']}, Progress: {job_status.get('progress', 0)}%"
            )

            if job_status["status"] == "completed":
                video_url = job_status["result"]["video_url"]
                print(f"\n✓ Video ready!")
                print(f"  URL: {video_url[:80]}...")
                print(f"  File size: {job_status['result']['file_size']} bytes")
                break
            elif job_status["status"] == "failed":
                print(f"\n✗ Video generation failed: {job_status.get('error')}")
                break

            time.sleep(15)

    client.close()


def example_wait_for_video():
    """Example 2: Using wait_for_video_job helper"""
    print("\n" + "=" * 60)
    print("Example 2: Using wait_for_video_job Helper")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation
    response = client.videos(
        prompt="A cool cat on a motorcycle at night",
        model="openai/sora-2",
        duration=4,
        size="1280x720",
    )

    job_id = response["data"]["job_id"]
    print(f"Job created: {job_id}")

    # Wait for completion (automatic polling)
    print("\nWaiting for completion...")
    try:
        final_status = client.wait_for_video_job(job_id, check_interval=15)

        video_url = final_status["result"]["video_url"]
        print(f"\n✓ Video ready!")
        print(f"  URL: {video_url[:80]}...")

    except TimeoutError as e:
        print(f"\n✗ Timeout: {str(e)}")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

    client.close()


def example_with_progress_callback():
    """Example 3: Progress monitoring with callback"""
    print("\n" + "=" * 60)
    print("Example 3: Progress Callback")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation
    response = client.videos(
        prompt="A futuristic city at sunset",
        model="openai/sora-2",
        duration=4,
    )

    job_id = response["data"]["job_id"]

    # Define progress callback
    def on_progress(status):
        progress = status.get("progress", 0)
        current_status = status["status"]
        print(f"  → {current_status}: {progress}% complete")

    # Wait with progress updates
    print("\nGenerating video...")
    try:
        final_status = client.wait_for_video_job(
            job_id,
            check_interval=10,
            callback=on_progress,
        )

        print(f"\n✓ Video ready: {final_status['result']['video_url'][:80]}...")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

    client.close()


def example_list_jobs():
    """Example 4: List all video jobs"""
    print("\n" + "=" * 60)
    print("Example 4: List Video Jobs")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Get all jobs
    jobs_response = client.list_video_jobs(limit=10)

    print(f"Total jobs: {jobs_response['total']}")
    print("\nJobs:")

    for job in jobs_response["jobs"]:
        print(f"\n  Job ID: {job['job_id']}")
        print(f"  Status: {job['status']}")
        print(f"  Model: {job['model']}")
        print(f"  Prompt: {job['prompt'][:50]}...")
        print(f"  Created: {job['created_at']}")

        if job["status"] == "completed" and "result" in job:
            print(f"  Video: {job['result']['video_url'][:60]}...")

    client.close()


def example_cancel_job():
    """Example 5: Cancel a pending job"""
    print("\n" + "=" * 60)
    print("Example 5: Cancel Job")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation
    response = client.videos(
        prompt="Test video",
        model="openai/sora-2",
        duration=4,
    )

    job_id = response["data"]["job_id"]
    print(f"Job created: {job_id}")

    # Cancel immediately (for demonstration)
    print("\nCancelling job...")
    try:
        result = client.cancel_video_job(job_id)
        print(f"✓ {result['message']}")
    except Exception as e:
        print(f"✗ Cancel failed: {str(e)}")

    client.close()


def example_comparison_google_vs_openai():
    """Example 6: Compare Google (sync) vs OpenAI (async)"""
    print("\n" + "=" * 60)
    print("Example 6: Google (Sync) vs OpenAI (Async)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    print("\n--- Google Veo (Synchronous) ---")
    print("Making request...")
    start_time = time.time()

    google_response = client.videos(
        prompt="A scenic landscape",
        model="google/veo-3.0-generate-001",
        duration=6,
    )

    google_time = time.time() - start_time
    print(f"✓ Completed in {google_time:.1f} seconds")
    print(f"  Video URL: {google_response['data'][0]['url'][:60]}...")
    print("  Note: Request blocked until video was ready")

    print("\n--- OpenAI Sora (Asynchronous) ---")
    print("Making request...")
    start_time = time.time()

    openai_response = client.videos(
        prompt="A scenic landscape",
        model="openai/sora-2",
        duration=4,
    )

    initial_time = time.time() - start_time
    print(f"✓ Initial response in {initial_time:.1f} seconds")

    job_id = openai_response["data"]["job_id"]
    print(f"  Job ID: {job_id}")
    print("  Note: Request returned immediately!")

    print("\nPolling for completion...")
    final_status = client.wait_for_video_job(job_id)
    total_time = time.time() - start_time

    print(f"✓ Video ready in {total_time:.1f} seconds total")
    print(f"  Video URL: {final_status['result']['video_url'][:60]}...")

    client.close()


def example_different_sizes():
    """Example 7: Different video sizes"""
    print("\n" + "=" * 60)
    print("Example 7: Different Video Sizes")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    sizes = [
        ("1280x720", "Landscape 720p"),
        ("720x1280", "Portrait 720p"),
    ]

    for size, description in sizes:
        print(f"\n--- {description} ({size}) ---")

        response = client.videos(
            prompt="A beautiful sunset",
            model="openai/sora-2",
            duration=4,
            size=size,
        )

        job_id = response["data"]["job_id"]
        print(f"Job created: {job_id}")

        # Wait for completion
        final_status = client.wait_for_video_job(job_id)
        print(f"✓ Video ready: {final_status['result']['video_url'][:60]}...")

    client.close()


def example_error_handling():
    """Example 8: Error handling"""
    print("\n" + "=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    from indoxhub import InsufficientCreditsError, InvalidParametersError

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    try:
        # Try invalid duration
        response = client.videos(
            prompt="Test",
            model="openai/sora-2",
            duration=100,  # Invalid - max is 12
        )

        if response["data"].get("is_async"):
            job_id = response["data"]["job_id"]
            final_status = client.wait_for_video_job(job_id)

    except InvalidParametersError as e:
        print(f"✗ Invalid parameters: {str(e)}")
    except InsufficientCreditsError as e:
        print(f"✗ Insufficient credits: {str(e)}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    client.close()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OPENAI ASYNC VIDEO GENERATION EXAMPLES")
    print("=" * 60)

    print("\nKey Differences:")
    print("  • Google Veo: Synchronous - waits until video is ready")
    print("  • OpenAI Sora: Asynchronous - returns job_id immediately")
    print("\nBenefits of Async:")
    print("  ✓ Instant response (no waiting)")
    print("  ✓ Can check status anytime")
    print("  ✓ Better for long-running generations")
    print("  ✓ Can cancel if needed")

    # Check API key
    if not os.getenv("INDOX_ROUTER_API_KEY"):
        print("\n⚠️  Please set INDOX_ROUTER_API_KEY environment variable")
        print("   export INDOX_ROUTER_API_KEY='your-api-key-here'")
        return

    # Examples
    examples = [
        ("Basic Async Video", example_basic_async_video),
        ("Wait for Video Helper", example_wait_for_video),
        ("Progress Callback", example_with_progress_callback),
        ("List Jobs", example_list_jobs),
        ("Cancel Job", example_cancel_job),
        ("Google vs OpenAI", example_comparison_google_vs_openai),
        ("Different Sizes", example_different_sizes),
        ("Error Handling", example_error_handling),
    ]

    print("\n" + "=" * 60)
    print("Choose an example:")
    print("=" * 60)
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all")
    print("=" * 60)

    try:
        choice = input("\nChoice (0-8): ").strip()

        if choice == "0":
            for name, func in examples:
                try:
                    func()
                    print("\n✅ Example completed")
                except Exception as e:
                    print(f"\n❌ Failed: {str(e)}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            _, func = examples[int(choice) - 1]
            func()
            print("\n✅ Example completed")
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
