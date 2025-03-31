# Image Generation Example

This example demonstrates how to use the IndoxRouter client to generate images from various AI providers.

## Basic Image Generation

```python
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Generate an image
response = client.images(
    prompt="A serene landscape with mountains and a lake at sunset",
    provider="openai",
    model="dall-e-3",
    size="1024x1024",
    n=1
)

# Print the response
print(f"Number of images: {len(response['images'])}")
print(f"Image URL: {response['images'][0]['url']}")
```

## Downloading and Saving the Generated Image

```python
import os
import requests
from PIL import Image
from io import BytesIO
from indoxrouter import Client

# Initialize client with API key
client = Client(api_key="your_api_key")

# Generate an image
response = client.images(
    prompt="A futuristic city with flying cars and neon lights",
    provider="openai",
    model="dall-e-3",
    size="1024x1024",
    n=1
)

# Download and save the image
if response.get("images") and len(response["images"]) > 0:
    image_url = response["images"][0].get("url")
    if image_url:
        print(f"Image URL: {image_url}")

        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))

        # Save the image
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_image.png")
        image.save(output_path)
        print(f"Image saved to {output_path}")
```

## Using Different Providers

Currently, image generation is primarily supported through OpenAI's DALL-E models:

```python
response = client.images(
    prompt="A serene landscape with mountains and a lake at sunset",
    provider="openai",
    model="dall-e-3",
    size="1024x1024",
    n=1
)
```

## Customizing Image Generation

You can customize the image generation by adjusting parameters:

```python
response = client.images(
    prompt="A serene landscape with mountains and a lake at sunset",
    provider="openai",
    model="dall-e-3",
    size="1792x1024",  # Different aspect ratio
    n=1,
    additional_params={
        "quality": "hd",  # Higher quality
        "style": "natural"  # Natural style
    }
)
```

## Error Handling

```python
from indoxrouter import Client
from indoxrouter.exceptions import ModelNotFoundError, ProviderNotFoundError, InvalidParametersError

try:
    client = Client(api_key="your_api_key")
    response = client.images(
        prompt="A serene landscape with mountains and a lake at sunset",
        provider="nonexistent",
        model="nonexistent-model"
    )
except ProviderNotFoundError as e:
    print(f"Provider not found: {e}")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except InvalidParametersError as e:
    print(f"Invalid parameters: {e}")
```
