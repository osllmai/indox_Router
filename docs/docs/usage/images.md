# Image Generation

IndoxRouter provides a unified interface for generating images from text prompts across various AI providers. This guide covers how to use the image generation capabilities.

## Basic Usage

The simplest way to generate images is with the `images()` method:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

# Generate an image
response = client.images(
    prompt="A serene mountain landscape with a lake at sunset",
    model="openai/dall-e-3"
)

# Get the image URL
image_url = response["data"][0]["url"]
print(f"Generated image URL: {image_url}")
```

## Model Selection

You can use different image generation models from various providers:

```python
# OpenAI DALL-E 3
dalle3_response = client.images(
    prompt="A futuristic city with flying cars",
    model="openai/dall-e-3"
)

# OpenAI DALL-E 2
dalle2_response = client.images(
    prompt="A futuristic city with flying cars",
    model="openai/dall-e-2"
)

# Stability AI
stability_response = client.images(
    prompt="A futuristic city with flying cars",
    model="stability/stable-diffusion-xl"
)
```

## Image Parameters

The image generation method accepts several parameters to control the output:

```python
response = client.images(
    prompt="A photorealistic portrait of a cyberpunk character",
    model="openai/dall-e-3",
    size="1024x1024",  # Image dimensions
    n=1,               # Number of images to generate
    quality="hd",      # Image quality (standard or hd)
    style="vivid"      # Image style (vivid or natural)
)
```

### Common Parameters

- `prompt`: The text description of the image to generate
- `model`: The model to use in format `provider/model_name`
- `size`: Image dimensions in format `widthxheight` (e.g., "1024x1024", "512x512")
- `n`: Number of images to generate
- `quality`: Image quality level (model dependent)
- `style`: Image style (model dependent)

## BYOK (Bring Your Own Key) Support

IndoxRouter supports BYOK for image generation, allowing you to use your own API keys for AI providers:

```python
# Use your own OpenAI API key for DALL-E 3
response = client.images(
    prompt="A futuristic cityscape at sunset",
    model="openai/dall-e-3",
    size="1024x1024",
    byok_api_key="sk-your-openai-key-here"
)
```

### BYOK Benefits for Image Generation

- **No Credit Deduction**: Your IndoxRouter credits remain unchanged
- **No Rate Limiting**: Bypass platform rate limits
- **Direct Provider Access**: Connect directly to your provider accounts
- **Cost Control**: Pay providers directly at their rates
- **Full Features**: Access to all provider-specific image generation features
- **Higher Quality**: Use provider's native image generation capabilities

## Response Format

The response from the images method follows this structure:

```python
{
    "created": 1684939249,
    "data": [
        {
            "url": "https://example.com/generated-image-123.png",
            "revised_prompt": "A serene mountain landscape with a crystal-clear lake reflecting the sunset colors, surrounded by pine trees and snow-capped peaks",
            "index": 0
        }
        # More items if n > 1
    ]
}
```

## Saving Generated Images

To save the generated images locally:

```python
import requests
import os

def save_image(url, filename):
    """Download and save an image from URL to a local file."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {filename}")
    else:
        print(f"Failed to download image: {response.status_code}")

# Generate an image
response = client.images(
    prompt="A colorful abstract painting with geometric shapes",
    model="openai/dall-e-3"
)

# Save each generated image
os.makedirs("generated_images", exist_ok=True)
for i, item in enumerate(response["data"]):
    image_url = item["url"]
    filename = f"generated_images/image_{i}.png"
    save_image(image_url, filename)
```

## Advanced Usage

### Generating Variations

Some models support generating variations of existing images. This feature may be added in the future.

### Image-to-Image Generation

Some models support image-to-image generation, where an input image is transformed based on a prompt. This feature may be added in the future.

## Examples

### Detailed Art Generation

```python
# Generate a detailed art piece
art_response = client.images(
    prompt=(
        "An intricate fantasy illustration of an ancient library filled with "
        "magical books, glowing orbs of light floating through the air, towering "
        "bookshelves reaching into a starry sky ceiling, and a wizard studying "
        "at an ornate desk"
    ),
    model="openai/dall-e-3",
    size="1024x1024",
    quality="hd",
    style="vivid"
)

print(f"Image URL: {art_response['data'][0]['url']}")
print(f"Revised prompt: {art_response['data'][0].get('revised_prompt', 'Not available')}")
```

### Product Visualization

```python
# Generate a product visualization
product_response = client.images(
    prompt=(
        "A professional product photography shot of a minimalist smartwatch "
        "with a sleek black band and circular face displaying a digital time "
        "against a clean white background, studio lighting"
    ),
    model="openai/dall-e-3",
    size="1024x1024",
    quality="hd",
    style="natural"
)

print(f"Product image URL: {product_response['data'][0]['url']}")
```

### Architectural Concept

```python
# Generate an architectural concept
architecture_response = client.images(
    prompt=(
        "A modern, sustainable treehouse design integrated into a forest canopy, "
        "featuring large windows, solar panels, natural wood materials, "
        "and connected walkways between tree platforms"
    ),
    model="openai/dall-e-3",
    size="1024x1024"
)

print(f"Architecture concept URL: {architecture_response['data'][0]['url']}")
```

## Best Practices

1. **Be detailed and specific**: The more detailed your prompt, the better the results
2. **Consider the style**: Specify the artistic style, medium, lighting, and mood
3. **Experiment with parameters**: Try different models, sizes, and quality settings
4. **Use appropriate models**: Choose models based on your needs and budget
5. **Review revised prompts**: Some models provide revised prompts that can help you understand how your prompt was interpreted

## Limitations

- Image generation capabilities may vary depending on the provider and model
- Some providers may have content filters that restrict certain types of content
- Image quality and adherence to the prompt varies across different models
- Costs for image generation can be higher than text generation

_Last updated: Nov 11, 2025_