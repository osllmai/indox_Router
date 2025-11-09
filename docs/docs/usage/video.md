# Video Generation

IndoxRouter provides a unified interface for generating videos from text prompts across various AI providers. This guide covers how to use the video generation capabilities with support for different models from Google, OpenAI, and Amazon.

## Basic Usage

The simplest way to generate videos is with the `videos()` method:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

# Generate a video (async operation)
response = client.videos(
    prompt="A serene mountain landscape with a lake at sunset, cinematic camera movement",
    model="openai/sora-2"
)

# Get the job status
print(f"Job ID: {response['data']['job_id']}")
print(f"Status: {response['data']['status']}")
```

## Understanding Video Generation

Video generation is typically an **asynchronous operation**. Unlike image generation which returns results immediately, video generation creates a job that you can monitor for completion:

```python
# Check job status
status_response = client.jobs(job_id="your_job_id")
print(f"Status: {status_response['status']}")
print(f"Progress: {status_response['progress']}%")

# Once completed, get the video URL
if status_response['status'] == 'completed':
    video_url = status_response['result']['data'][0]['url']
    print(f"Video URL: {video_url}")
```

## Model Selection

You can use different video generation models from various providers:

### OpenAI Sora Models

```python
# Sora 2 (recommended for most use cases)
sora_response = client.videos(
    prompt="A cat playing piano in a jazz club",
    model="openai/sora-2",
    size="1280x720",
    seconds=4
)

# Sora 2 Pro (higher quality, more expensive)
sora_pro_response = client.videos(
    prompt="A cinematic battle scene with dramatic lighting",
    model="openai/sora-2-pro",
    size="1792x1024",
    seconds=8
)
```

### Google Veo Models

```python
# Veo 2 (text-to-video and image-to-video)
veo2_response = client.videos(
    prompt="A butterfly emerging from its chrysalis",
    model="google/veo-2.0-generate-001",
    aspect_ratio="16:9",
    duration=6
)

# Veo 3 (with optional audio generation)
veo3_response = client.videos(
    prompt="A chef preparing pasta in an Italian kitchen",
    model="google/veo-3.0-generate-001",
    aspect_ratio="16:9",
    duration=8,
    generate_audio=True  # Include synchronized audio
)

# Veo 3.1 (advanced features)
veo31_response = client.videos(
    prompt="A futuristic city with flying cars",
    model="google/veo-3.1-generate-preview",
    aspect_ratio="16:9",
    duration=8,
    generate_audio=True,
    negative_prompt="blurry, low quality, static",
    person_generation="allow_all"
)
```

### Amazon Nova Reel

```python
# Amazon Nova Reel (cost-effective option)
nova_response = client.videos(
    prompt="A timelapse of a flower blooming",
    model="amazon/nova-reel",
    duration=6
)
```

## Video Parameters

The video generation method accepts several parameters to control the output:

### Core Parameters

```python
response = client.videos(
    prompt="A majestic eagle soaring over mountain peaks",  # Required: text description
    model="openai/sora-2",                                # Required: provider/model format
    size="1280x720",                                      # Video resolution/dimensions
    duration=4,                                           # Video duration in seconds
    n=1,                                                  # Number of videos to generate
    aspect_ratio="16:9",                                  # Video aspect ratio
    fps=24,                                               # Frames per second
    seed=42                                               # Random seed for reproducibility
)
```

### Provider-Specific Parameters

#### OpenAI Sora Parameters

```python
sora_response = client.videos(
    prompt="A ballet dancer performing in a spotlight",
    model="openai/sora-2",
    size="1280x720",        # 1280x720 or 720x1280
    seconds=4,              # 4, 8, or 12 seconds
    input_image="data:image/png;base64,...",  # Optional: base64 image for image-to-video
    input_reference="data:image/png;base64,..."  # Optional: reference image
)
```

#### Google Veo Parameters

```python
veo_response = client.videos(
    prompt="A serene underwater scene with colorful fish",
    model="google/veo-3.0-generate-001",
    aspect_ratio="16:9",                    # 16:9 or 9:16
    resolution="720p",                      # 720p or 1080p (Veo 3+)
    duration=8,                             # 4-8 seconds depending on model
    generate_audio=True,                    # Generate synchronized audio
    input_image="data:image/png;base64,...", # Image-to-video input
    reference_image="data:image/png;base64,...", # Reference image for style
    reference_images=["data:image/png;base64,...", "data:image/png;base64,..."], # Multiple references (Veo 3.1)
    negative_prompt="blurry, distorted, low quality", # What to avoid (Veo 3.1)
    person_generation="allow_adult",         # Person generation control (Veo 3.1)
    last_frame="data:image/png;base64,...", # Frame interpolation (Veo 3.1)
    video="data:video/mp4;base64,..."       # Video extension input (future)
)
```

#### Amazon Nova Reel Parameters

```python
nova_response = client.videos(
    prompt="A cup of coffee steaming on a wooden table",
    model="amazon/nova-reel",
    dimension="1280x720",    # Fixed: 1280x720
    duration_seconds=6,      # Fixed: 6 seconds
    fps=24,                  # Fixed: 24 fps
    seed=123,                # Random seed
    input_image="data:image/png;base64,..." # Optional: base64 image input
)
```

## Job Monitoring and Results

### Checking Job Status

```python
# Get job status
job_response = client.jobs(job_id="your_job_id")

print(f"Job Status: {job_response['status']}")
print(f"Progress: {job_response['progress']}%")
print(f"Created: {job_response['created_at']}")

if job_response['status'] == 'completed':
    # Access the generated video
    video_data = job_response['result']['data'][0]
    video_url = video_data['url']
    print(f"Video URL: {video_url}")
elif job_response['status'] == 'failed':
    print(f"Error: {job_response.get('error', 'Unknown error')}")
```

### Response Structure

Completed video generation returns:

```python
{
    "job_id": "video_job_123456",
    "status": "completed",
    "progress": 100,
    "created_at": "2024-01-15T10:30:00Z",
    "result": {
        "data": [
            {
                "url": "https://example.com/generated-video-123.mp4",
                "s3_key": "user_123/video/video_456.mp4",
                "file_size": 5242880,
                "content_type": "video/mp4",
                "file_name": "video_456.mp4"
            }
        ],
        "model": "openai/sora-2",
        "created": 1705312200
    }
}
```

## Saving Generated Videos

To save the generated videos locally:

```python
import requests
import os

def save_video(url, filename):
    """Download and save a video from URL to a local file."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video saved as {filename}")
    else:
        print(f"Failed to download video: {response.status_code}")

# Check if job is completed
job_response = client.jobs(job_id="your_job_id")

if job_response['status'] == 'completed':
    # Save each generated video
    os.makedirs("generated_videos", exist_ok=True)
    for i, video_item in enumerate(job_response['result']['data']):
        video_url = video_item['url']
        filename = f"generated_videos/video_{i}.mp4"
        save_video(video_url, filename)
else:
    print("Video generation not yet completed")
```

## Advanced Features

### Image-to-Video Generation

Transform existing images into videos:

```python
# OpenAI Sora with image input
image_video_response = client.videos(
    prompt="Make this image come alive with gentle movement and flowing water",
    model="openai/sora-2",
    input_image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",  # Base64 encoded image
    size="1280x720",
    seconds=4
)

# Google Veo with image input
veo_image_response = client.videos(
    prompt="Animate this landscape with a gentle breeze and moving clouds",
    model="google/veo-3.0-generate-001",
    input_image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    aspect_ratio="16:9",
    duration=8,
    generate_audio=True
)
```

### Reference Images and Style Control

Use reference images to guide generation:

```python
# Google Veo 3.1 with multiple reference images
styled_response = client.videos(
    prompt="A ballet dancer in the style of these reference images",
    model="google/veo-3.1-generate-preview",
    reference_images=[
        "data:image/png;base64,...",  # Reference image 1
        "data:image/png;base64,...",  # Reference image 2
        "data:image/png;base64,..."   # Reference image 3
    ],
    aspect_ratio="9:16",
    duration=8,
    generate_audio=True
)
```

### Audio Generation

Generate videos with synchronized audio:

```python
# Google Veo 3+ with audio
audio_video_response = client.videos(
    prompt="A musician playing guitar on a beach at sunset",
    model="google/veo-3.0-generate-001",
    aspect_ratio="16:9",
    duration=8,
    generate_audio=True  # Generates music and sound effects
)
```

### Frame Interpolation and Video Extension

Advanced features in Google Veo 3.1:

```python
# Frame interpolation between two frames
interpolation_response = client.videos(
    prompt="Smooth transition between these two poses",
    model="google/veo-3.1-fast-generate-preview",
    input_image="data:image/png;base64,...",  # Starting frame
    last_frame="data:image/png;base64,...",   # Ending frame
    duration=8,
    generate_audio=True
)
```

## BYOK (Bring Your Own Key) Support

IndoxRouter supports BYOK for video generation:

```python
# Use your own OpenAI API key
response = client.videos(
    prompt="A rocket launching into space",
    model="openai/sora-2",
    size="1280x720",
    seconds=4,
    byok_api_key="sk-your-openai-key-here"
)

# Use your own Google API key
google_response = client.videos(
    prompt="A butterfly emerging from its chrysalis",
    model="google/veo-3.0-generate-001",
    aspect_ratio="16:9",
    duration=8,
    byok_api_key="your-google-api-key-here"
)
```

### BYOK Benefits for Video Generation

- **No Credit Deduction**: Your IndoxRouter credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific video generation features

## Examples

### Cinematic Scene Generation

```python
# Create a cinematic video scene
cinematic_response = client.videos(
    prompt=(
        "A dramatic cinematic scene: a lone warrior standing on a cliff "
        "overlooking a vast ocean at sunset, wind blowing through their "
        "hair, camera slowly dollying in for an emotional close-up, "
        "epic orchestral music swelling in the background"
    ),
    model="openai/sora-2-pro",
    size="1792x1024",
    seconds=8
)
```

### Product Showcase Video

```python
# Generate a product showcase
product_video = client.videos(
    prompt=(
        "A sleek smartphone rotating slowly on a pedestal, "
        "highlighting its premium design and features, "
        "soft studio lighting, professional product photography style"
    ),
    model="google/veo-3.0-generate-001",
    aspect_ratio="9:16",  # Vertical video for social media
    duration=6,
    generate_audio=False
)
```

### Educational Animation

```python
# Create an educational animation
educational_video = client.videos(
    prompt=(
        "Animated explanation of photosynthesis: show a green plant "
        "absorbing sunlight, water molecules moving up through roots, "
        "carbon dioxide entering leaves, oxygen and glucose being produced, "
        "simple animated style suitable for children"
    ),
    model="amazon/nova-reel",
    duration=6
)
```

## Best Practices

1. **Be descriptive**: Provide detailed, vivid descriptions of scenes, actions, camera movements, and atmosphere
2. **Consider timing**: Shorter videos (4-6 seconds) often work better than longer ones
3. **Specify camera work**: Include camera movement directions like "slow pan", "dolly in", "tracking shot"
4. **Think about audio**: For models with audio generation, consider what sounds would enhance the scene
5. **Use appropriate aspect ratios**: 16:9 for horizontal, 9:16 for vertical/social media
6. **Start simple**: Begin with basic prompts and gradually add complexity
7. **Monitor progress**: Video generation can take time - use job monitoring to track progress

## Limitations and Considerations

### General Limitations

- **Asynchronous processing**: Video generation is not immediate - jobs can take minutes to hours
- **Cost**: Video generation is significantly more expensive than image generation
- **File sizes**: Generated videos can be large (5-50MB depending on duration and resolution)
- **Content filtering**: All providers have safety filters that may reject certain content
- **Quality variation**: Results can vary between providers and even between runs

### Provider-Specific Considerations

#### OpenAI Sora

- Limited to 4, 8, or 12 second videos
- Best at cinematic and realistic scenes
- Supports image-to-video input

#### Google Veo

- Excellent at smooth motion and realistic videos
- Supports audio generation with music and sound effects
- Advanced features like reference images and frame interpolation (Veo 3.1)
- Best for high-quality, cinematic content

#### Amazon Nova Reel

- Most cost-effective option
- Fixed 6-second, 720p videos
- Good for simple animations and product showcases
- Fastest generation times

## Troubleshooting

### Common Issues

**Job Stuck in "queued" or "processing"**: This is normal - video generation takes time. Continue checking the job status.

**Generation Failed**: Check the error message in the job response. Common causes:

- Prompt violates safety filters
- Invalid parameters for the selected model
- Provider service issues

**Low Quality Results**: Try:

- More detailed prompts
- Different models
- Adjusting parameters like duration or resolution

**Audio Not Generated**: Ensure you're using a model that supports audio generation (Google Veo 3+) and have `generate_audio=True`.

### Getting Help

If you encounter issues:

1. Check the job error message: `client.jobs(job_id)["error"]`
2. Verify your parameters match the model's specifications
3. Try a different model or simplify your prompt
4. Contact support if the issue persists

_Last updated: Nov 08, 2025_