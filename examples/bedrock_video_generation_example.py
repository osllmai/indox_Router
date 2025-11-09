"""
AWS Bedrock Video Generation Examples

This script demonstrates how to use IndoxRouter's Bedrock video generation
with Amazon Nova Reel and Luma Ray2 models.

Bedrock video generation is ASYNCHRONOUS - the request returns immediately
with a job_id, and you poll for completion. The video is stored in S3.

Requirements:
    pip install indoxrouter

Set your API key:
    export INDOX_ROUTER_API_KEY="your-api-key-here"
"""

from indoxrouter import Client
import os
import time


def example_amazon_nova_reel():
    """Example 1: Amazon Nova Reel video generation"""
    print("\n" + "=" * 60)
    print("Example 1: Amazon Nova Reel (Bedrock)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation (returns immediately)
    response = client.videos(
        prompt="a person running from a police officer in soccer field",
        model="amazon/nova-reel-v1",
        duration=6,
        size="1280x720",
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
        print(f"  Invocation ARN: {response['data']['provider_video_id']}")

        # Wait for completion (automatic polling)
        print("\nWaiting for completion...")
        try:
            final_status = client.wait_for_video_job(job_id, check_interval=20)

            video_url = final_status["result"]["video_url"]
            print(f"\n✓ Video ready!")
            print(f"  URL: {video_url[:80]}...")
            print(f"  File size: {final_status['result']['file_size']} bytes")

        except TimeoutError as e:
            print(f"\n✗ Timeout: {str(e)}")
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")

    client.close()


def example_luma_ray2():
    """Example 2: Luma Ray2 video generation"""
    print("\n" + "=" * 60)
    print("Example 2: Luma Ray2 (Bedrock)")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Start video generation
    response = client.videos(
        prompt="A cool cat on a motorcycle at night",
        model="luma/ray-v2",
        duration=6,
        size="1280x720",
    )

    job_id = response["data"]["job_id"]
    print(f"Job created: {job_id}")

    # Wait for completion with progress callback
    def on_progress(status):
        progress = status.get("progress", 0)
        current_status = status["status"]
        print(f"  → {current_status}: {progress}% complete")

    print("\nGenerating video...")
    try:
        final_status = client.wait_for_video_job(
            job_id,
            check_interval=20,
            callback=on_progress,
        )

        print(f"\n✓ Video ready: {final_status['result']['video_url'][:80]}...")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

    client.close()


def example_nova_with_image_input():
    """Example 3: Amazon Nova Reel with image input"""
    print("\n" + "=" * 60)
    print("Example 3: Nova Reel with Image Input")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # You would need to provide a base64-encoded image here
    # For demonstration purposes, this is a placeholder
    print("Note: This example requires a base64-encoded image")
    print("Skipping actual execution")

    # Example usage (with actual image):
    # input_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANS..."
    #
    # response = client.videos(
    #     prompt="Continue the scene from this image",
    #     model="amazon/nova-reel-v1",
    #     duration=6,
    #     input_image=input_image_base64,
    # )

    client.close()


def example_cost_comparison():
    """Example 4: Cost comparison between models"""
    print("\n" + "=" * 60)
    print("Example 4: Cost Comparison")
    print("=" * 60)

    print("\nAmazon Nova Reel:")
    print("  - Resolution: 1280x720 (720p)")
    print("  - Duration: 6 seconds (fixed)")
    print("  - Cost: $0.08 per second")
    print("  - Total: $0.48 per video")
    print("  - Performance: Standard quality")

    print("\nLuma Ray2:")
    print("  - Resolution: 1280x720 (720p)")
    print("  - Duration: 6 seconds (fixed)")
    print("  - Cost: $1.50 per second")
    print("  - Total: $9.00 per video")
    print("  - Performance: Higher quality")

    print("\n  - Resolution: 960x540 (540p)")
    print("  - Duration: 6 seconds (fixed)")
    print("  - Cost: $0.75 per second")
    print("  - Total: $4.50 per video")
    print("  - Performance: Standard quality")

    print("\nRecommendation:")
    print("  - For cost-effective videos: Amazon Nova Reel")
    print("  - For premium quality: Luma Ray2 720p")
    print("  - For balance: Luma Ray2 540p")


def example_list_jobs():
    """Example 5: List all video jobs"""
    print("\n" + "=" * 60)
    print("Example 5: List Video Jobs")
    print("=" * 60)

    client = Client(api_key=os.getenv("INDOX_ROUTER_API_KEY"))

    # Get all jobs
    jobs_response = client.list_video_jobs(limit=10)

    print(f"Total jobs: {jobs_response['total']}")
    print("\nJobs:")

    for job in jobs_response["jobs"]:
        print(f"\n  Job ID: {job['job_id']}")
        print(f"  Provider: {job['provider']}")
        print(f"  Status: {job['status']}")
        print(f"  Model: {job['model']}")
        print(f"  Prompt: {job['prompt'][:50]}...")
        print(f"  Created: {job['created_at']}")

        if job["status"] == "completed" and "result" in job:
            print(f"  Video: {job['result']['video_url'][:60]}...")

    client.close()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("AWS BEDROCK VIDEO GENERATION EXAMPLES")
    print("=" * 60)

    print("\nSupported Models:")
    print("  • Amazon Nova Reel: amazon/nova-reel-v1")
    print("  • Luma Ray2: luma/ray-v2")

    print("\nKey Features:")
    print("  ✓ Asynchronous generation (instant response)")
    print("  ✓ Automatic S3 storage")
    print("  ✓ Job status polling")
    print("  ✓ Fixed 6-second duration")
    print("  ✓ Multiple resolution options")

    # Check API key
    if not os.getenv("INDOX_ROUTER_API_KEY"):
        print("\n⚠️  Please set INDOX_ROUTER_API_KEY environment variable")
        print("   export INDOX_ROUTER_API_KEY='your-api-key-here'")
        return

    # Examples
    examples = [
        ("Amazon Nova Reel", example_amazon_nova_reel),
        ("Luma Ray2", example_luma_ray2),
        ("Nova with Image Input", example_nova_with_image_input),
        ("Cost Comparison", example_cost_comparison),
        ("List Jobs", example_list_jobs),
    ]

    print("\n" + "=" * 60)
    print("Choose an example:")
    print("=" * 60)
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all")
    print("=" * 60)

    try:
        choice = input("\nChoice (0-5): ").strip()

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
