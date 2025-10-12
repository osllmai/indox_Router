# Vision & Multimodal Capabilities

IndoxRouter supports vision-capable models that can understand and analyze images alongside text. This guide covers how to send images to AI models and work with multimodal content.

## Supported Models

Many models across different providers support image inputs. Here are some popular vision-capable models:

### OpenAI

- `gpt-4o` - Most capable multimodal model
- `gpt-4o-mini` - Fast and cost-effective vision model
- `gpt-4.1` - Latest GPT-4 with vision
- `gpt-4.1-mini` - Efficient GPT-4.1 with vision
- `chatgpt-4o` - ChatGPT optimized vision model
- `o1` - Advanced reasoning with vision

### Anthropic

- `claude-sonnet-4.5` - Sonnet 4.5 with vision
- `claude-sonnet-4` - Sonnet 4 with vision
- `claude-opus-4.1` - Most capable Claude with vision
- `claude-3-opus-20240229` - Claude 3 Opus
- `claude-3-sonnet-20240229` - Claude 3 Sonnet
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet
- `claude-3-haiku-20240307` - Fast and efficient with vision

### Google

- `gemini-2.5-flash-preview` - Latest Gemini Flash
- `gemini-2.5-pro-preview` - Latest Gemini Pro
- `gemini-2.0-flash` - Gemini 2.0 Flash
- `gemini-1.5-pro` - Gemini 1.5 Pro
- `gemini-1.5-flash` - Fast Gemini with vision
- `gemma-3-27b` - Open Gemma model with vision

### Amazon Bedrock

- `amazon.nova-lite-v1:0` - Nova Lite with vision
- `amazon.nova-pro-v1:0` - Nova Pro with vision

### Meta

- `meta.llama3-2-11b-instruct-v1:0` - Llama 3.2 11B Vision
- `meta.llama3-2-90b-instruct-v1:0` - Llama 3.2 90B Vision

## Image Input Format

IndoxRouter uses a standardized format for multimodal content. Images are sent as part of the message content array.

### Basic Image with Text

```python
from indoxrouter import Client
import base64

# Initialize client
client = Client(api_key="your_api_key")

# Read and encode image
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

# Send request with image
response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image",
                    "image": {
                        "data": image_base64,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="openai/gpt-4o"
)

print(response["data"])
```

### Image from URL

You can also send images via URL (supported by most providers):

```python
response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image"
                },
                {
                    "type": "image",
                    "image": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ],
    model="anthropic/claude-sonnet-4.5"
)
```

## Multiple Images

You can include multiple images in a single request:

```python
import base64

# Read multiple images
with open("image1.jpg", "rb") as f:
    image1_base64 = base64.b64encode(f.read()).decode('utf-8')

with open("image2.jpg", "rb") as f:
    image2_base64 = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Compare these two images. What are the main differences?"
                },
                {
                    "type": "image",
                    "image": {
                        "data": image1_base64,
                        "media_type": "image/jpeg"
                    }
                },
                {
                    "type": "image",
                    "image": {
                        "data": image2_base64,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="google/gemini-2.5-pro-preview"
)

print(response["data"])
```

## Supported Image Formats

The following image formats are supported:

- **JPEG** (`image/jpeg`)
- **PNG** (`image/png`)
- **WebP** (`image/webp`)
- **GIF** (`image/gif`) - Some models only

!!! note "Image Format Recommendations" - Use **JPEG** for photographs and complex images - Use **PNG** for screenshots, diagrams, and images with text - Use **WebP** for smaller file sizes with good quality - Convert images to JPEG or PNG for best compatibility

## Image Size Limits

IndoxRouter enforces the following limits to ensure optimal performance:

- **Maximum single image size**: 20MB (raw bytes)
- **Maximum total images per request**: 100MB (all images combined)

!!! warning "Size Limit Enforcement"
If your images exceed these limits, you'll receive a `400 Bad Request` error. Compress or resize images before sending.

### Image Optimization Tips

```python
from PIL import Image
import io
import base64

def optimize_image(image_path, max_size_mb=2):
    """
    Optimize an image to reduce size while maintaining quality.

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum size in megabytes (default: 2MB)

    Returns:
        Base64 encoded optimized image
    """
    img = Image.open(image_path)

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Resize if image is very large
    max_dimension = 2048
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Save with optimization
    buffer = io.BytesIO()
    quality = 85

    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_mb = buffer.tell() / (1024 * 1024)

        if size_mb <= max_size_mb or quality <= 20:
            break
        quality -= 5

    # Encode to base64
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

# Use the optimized image
optimized_image = optimize_image("large_image.jpg", max_size_mb=2)

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image",
                    "image": {
                        "data": optimized_image,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="openai/gpt-4o-mini"
)
```

## Multi-Turn Conversations with Images

You can maintain conversations with images across multiple turns:

```python
import base64

# First turn with image
with open("diagram.png", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What does this diagram show?"},
            {
                "type": "image",
                "image": {
                    "data": image_base64,
                    "media_type": "image/png"
                }
            }
        ]
    }
]

response = client.chat(messages=messages, model="anthropic/claude-opus-4.1")
assistant_message = response["choices"][0]["message"]["content"]
print(f"Assistant: {assistant_message}")

# Add assistant response to conversation
messages.append({
    "role": "assistant",
    "content": assistant_message
})

# Follow-up question (no need to resend the image)
messages.append({
    "role": "user",
    "content": "Can you explain the flow in more detail?"
})

response = client.chat(messages=messages, model="anthropic/claude-opus-4.1")
print(f"Assistant: {response['choices'][0]['message']['content']}")
```

!!! tip "Image Memory"
Once an image is sent in a conversation, the model remembers it for subsequent turns. You don't need to resend the image unless you want to reference a different image.

## Common Use Cases

### 1. Document Analysis

```python
import base64

with open("invoice.pdf.jpg", "rb") as f:
    invoice_image = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract all the line items, quantities, and prices from this invoice."
                },
                {
                    "type": "image",
                    "image": {
                        "data": invoice_image,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="openai/gpt-4o"
)

print(response["data"])
```

### 2. Image Description for Accessibility

```python
import base64

with open("photo.jpg", "rb") as f:
    photo_base64 = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "system",
            "content": "You are an accessibility assistant. Provide detailed, accurate descriptions of images for visually impaired users."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please provide a detailed description of this image for a screen reader."
                },
                {
                    "type": "image",
                    "image": {
                        "data": photo_base64,
                        "media_type": "image/jpeg"
                    }
                }
            ]
        }
    ],
    model="google/gemini-2.0-flash"
)

print(response["data"])
```

### 3. Chart and Graph Analysis

```python
import base64

with open("sales_chart.png", "rb") as f:
    chart_image = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this sales chart and provide insights about trends, peaks, and anomalies."
                },
                {
                    "type": "image",
                    "image": {
                        "data": chart_image,
                        "media_type": "image/png"
                    }
                }
            ]
        }
    ],
    model="anthropic/claude-sonnet-4.5"
)

print(response["data"])
```

### 4. Code Screenshot Analysis

```python
import base64

with open("code_screenshot.png", "rb") as f:
    code_image = base64.b64encode(f.read()).decode('utf-8')

response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Review this code and suggest improvements. Identify any bugs or security issues."
                },
                {
                    "type": "image",
                    "image": {
                        "data": code_image,
                        "media_type": "image/png"
                    }
                }
            ]
        }
    ],
    model="openai/gpt-4o"
)

print(response["data"])
```

## Error Handling

### Model Doesn't Support Images

If you try to send an image to a text-only model, you'll receive an error:

```python
try:
    response = client.chat(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image",
                        "image": {"data": image_base64, "media_type": "image/jpeg"}
                    }
                ]
            }
        ],
        model="openai/gpt-3.5-turbo"  # Text-only model
    )
except Exception as e:
    print(f"Error: {e}")
    # Error: Model 'gpt-3.5-turbo' from provider 'openai' does not support image inputs.
    # Supported input modalities: text.
    # Please use a vision-capable model like 'gpt-4o', 'claude-3-sonnet-20240229', or 'gemini-1.5-pro'.
```

### Image Too Large

```python
try:
    # Very large image
    response = client.chat(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image"},
                    {
                        "type": "image",
                        "image": {"data": huge_image_base64, "media_type": "image/jpeg"}
                    }
                ]
            }
        ],
        model="openai/gpt-4o"
    )
except Exception as e:
    print(f"Error: {e}")
    # Error: Image size exceeds maximum allowed size of 20MB.
    # Please reduce the image size or resolution.
```

## Best Practices

### 1. Choose the Right Model

Different models have different strengths:

- **GPT-4o**: Best for general-purpose vision tasks, excellent text extraction
- **Claude Opus 4.1**: Excellent for detailed analysis and reasoning about images
- **Gemini 2.5 Pro**: Strong at multi-image comparison and video frames
- **GPT-4o-mini**: Fast and cost-effective for simple vision tasks

### 2. Optimize Images

- Resize large images to reasonable dimensions (e.g., 2048x2048 max)
- Compress images to reduce file size
- Use JPEG for photos, PNG for diagrams/screenshots
- Remove unnecessary metadata

### 3. Provide Clear Instructions

Be specific about what you want the model to analyze:

```python
# ❌ Vague
{"type": "text", "text": "What is this?"}

# ✅ Specific
{"type": "text", "text": "Identify all the people in this image and describe what they're doing."}
```

### 4. Use System Messages

Guide the model's behavior with system messages:

```python
messages = [
    {
        "role": "system",
        "content": "You are an expert medical image analyst. Provide detailed, technical descriptions."
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this X-ray image."},
            {"type": "image", "image": {"data": xray_base64, "media_type": "image/jpeg"}}
        ]
    }
]
```

### 5. Handle Errors Gracefully

Always wrap vision API calls in try-except blocks:

```python
try:
    response = client.chat(
        messages=[...],
        model="openai/gpt-4o"
    )
    print(response["data"])
except Exception as e:
    print(f"Failed to analyze image: {e}")
    # Implement fallback or retry logic
```

## Pricing Considerations

Vision models typically cost more than text-only models due to image processing:

- Images are tokenized and counted toward your usage
- Larger images use more tokens
- Multiple images increase costs proportionally

!!! tip "Cost Optimization" - Use smaller images when possible - Choose cost-effective models like `gpt-4o-mini` or `gemini-1.5-flash` for simple tasks - Use BYOK (Bring Your Own Key) for direct provider pricing

## BYOK with Vision Models

You can use your own API keys with vision models:

```python
response = client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image", "image": {"data": image_base64, "media_type": "image/jpeg"}}
            ]
        }
    ],
    model="openai/gpt-4o",
    byok_api_key="sk-your-openai-key"
)
```

## Streaming with Images

Vision models support streaming just like text-only models:

```python
import base64

with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

for chunk in client.chat(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail."},
                {"type": "image", "image": {"data": image_base64, "media_type": "image/jpeg"}}
            ]
        }
    ],
    model="anthropic/claude-sonnet-4.5",
    stream=True
):
    if isinstance(chunk, dict) and "data" in chunk:
        print(chunk["data"], end="", flush=True)
```

## Limitations

### Per-Provider Limitations

Different providers have different limitations:

- **OpenAI**: Up to 20 images per request (depending on model)
- **Anthropic**: Up to 20 images per request
- **Google**: Varies by model, generally supports multiple images
- **Image size**: Most providers limit images to ~20MB per image

### Quality Considerations

- Very small images may not be analyzed accurately
- Blurry or low-quality images may produce less accurate results
- Some models have difficulty with:
  - Very small text in images
  - Complex diagrams with many elements
  - Highly compressed or artifacted images

## Next Steps

- Explore [Chat Completions](chat.md) for general chat functionality
- Learn about [BYOK Support](byok.md) to use your own API keys
- Check [Rate Limits](rate-limits.md) for usage constraints
- See [Basic Examples](../examples/basic.md) for more code samples
