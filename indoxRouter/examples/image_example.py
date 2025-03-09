"""
Example of using the indoxRouter client for image generation.
"""

import os
import sys
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Add the parent directory to the path so we can import indoxrouter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indoxrouter import Client

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ.get("INDOXROUTER_API_KEY")
if not api_key:
    print("Please set the INDOXROUTER_API_KEY environment variable")
    sys.exit(1)

# Initialize the client
client = Client(api_key=api_key)

try:
    # Generate an image
    print("Generating image...")
    response = client.images(
        prompt="A serene landscape with mountains and a lake at sunset",
        provider="openai",
        model="dall-e-3",
        size="1024x1024",
        n=1,
    )

    # Print the response
    print("\nImage generation response:")
    print(f"Model: {response.get('model')}")
    print(f"Provider: {response.get('provider')}")
    print(f"Number of images: {len(response.get('images', []))}")

    # Download and display the image
    if response.get("images") and len(response["images"]) > 0:
        image_url = response["images"][0].get("url")
        if image_url:
            print(f"Image URL: {image_url}")

            # Download the image
            print("Downloading image...")
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))

            # Save the image
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "generated_image.png")
            image.save(output_path)
            print(f"Image saved to {output_path}")

            # Display the image if running in a Jupyter notebook
            try:
                from IPython.display import display

                display(image)
            except ImportError:
                print("To display the image, run this script in a Jupyter notebook")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the client
    client.close()
