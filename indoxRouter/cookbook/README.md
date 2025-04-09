# IndoxRouter Cookbook

This directory contains examples and recipes for using the IndoxRouter client to interact with various AI providers.

## Examples

- [Chat Completion](chat_completion.md): Examples of generating chat completions
- [Embeddings](embeddings.md): Examples of generating embeddings
- [Image Generation](image_generation.md): Examples of generating images

## Jupyter Notebook

- [IndoxRouter Cookbook](indoxRouter_cookbook.ipynb): A comprehensive Jupyter notebook with examples of using the IndoxRouter client

## Getting Started

To run these examples, you'll need to:

1. Install the IndoxRouter client:

```bash
pip install indoxrouter
```

2. Set your API key:

```bash
# Set environment variable
export INDOXROUTER_API_KEY=your-api-key

# Or provide it directly in your code
from indoxrouter import Client
client = Client(api_key="your-api-key")
```

3. Run the examples:

```bash
python -c "from indoxrouter import Client; client = Client(api_key='your_api_key'); print(client.chat([{'role': 'user', 'content': 'Hello!'}]))"
```

## Note on API Keys

The IndoxRouter API key is used to authenticate with the IndoxRouter server. You don't need to provide individual API keys for each provider (like OpenAI, Anthropic, etc.) as the IndoxRouter server handles that for you.
