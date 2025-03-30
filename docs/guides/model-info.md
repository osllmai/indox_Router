# Model Information System

IndoxRouter includes a model information system that provides information about AI models from various providers. This guide explains how the model information system works and how to use it.

## Overview

The model information system loads model information from JSON files in the `providers/json` directory. Each provider has its own JSON file containing information about its models, including capabilities, pricing, and other metadata.

## JSON File Structure

Each provider's JSON file contains an array of model objects. Each model object has the following structure:

```json
{
  "number": "1",
  "modelName": "gpt-4o-mini",
  "name": "GPT-4O Mini",
  "type": "Text Generation",
  "inputPricePer1KTokens": 0.00015,
  "outputPricePer1KTokens": 0.0006,
  "description": "GPT-4o mini enables a broad range of tasks with its low cost and latency...",
  "contextWindows": "128k Tokens",
  "recommended": true,
  "commercial": false,
  "pricey": false,
  "output": "16384 Tokens",
  "comments": "Fastest and most affordable flagship model.",
  "companyModelName": "Openai : GPT-4O Mini",
  "promptTemplate": "<|start_header_id|>user<|end_header_id|>\n\n%1<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n%2<|eot_id|>",
  "systemPrompt": ""
}
```

The most important fields for the model information system are:

- `modelName`: The name of the model
- `name`: The display name of the model
- `type`: The type of the model (e.g., "Text Generation", "Embedding", "Image Generation")
- `inputPricePer1KTokens`: The price per 1,000 tokens for input
- `outputPricePer1KTokens`: The price per 1,000 tokens for output
- `description`: A description of the model
- `contextWindows`: The context window size of the model
- `recommended`: Whether the model is recommended
- `commercial`: Whether the model is for commercial use
- `pricey`: Whether the model is expensive

## Model Information Module

The `model_info` module provides functions for loading and accessing model information:

### `load_provider_models(provider)`

Loads model information for a provider from its JSON file.

```python
from app.utils.model_info import load_provider_models

# Load model information for OpenAI
models = load_provider_models("openai")
```

### `get_model_info(provider, model_name)`

Gets information about a specific model.

```python
from app.utils.model_info import get_model_info

# Get information about GPT-4o Mini
model_info = get_model_info("openai", "gpt-4o-mini")
print(model_info["name"])  # GPT-4O Mini
print(model_info["inputPricePer1KTokens"])  # 0.00015
print(model_info["outputPricePer1KTokens"])  # 0.0006
```

### `calculate_cost(provider, model_name, tokens_prompt, tokens_completion)`

Calculates the cost of a request based on token usage.

```python
from app.utils.model_info import calculate_cost

# Calculate the cost of a request with 1,000 prompt tokens and 500 completion tokens
cost = calculate_cost("openai", "gpt-4o-mini", 1000, 500)
print(cost)  # 0.00045
```

## Using Model Information in Resources

The resource classes (Chat, Completions, Embeddings, and Images) use the model information system to calculate the cost of each request. The cost is calculated using the `calculate_cost` function from the `model_info` module.

For example, in the Chat resource:

```python
# Calculate cost based on token usage and model information
cost = calculate_cost(
    provider=provider,
    model_name=model_name,
    tokens_prompt=tokens_prompt,
    tokens_completion=tokens_completion
)
```

## Adding New Models

To add a new model, you need to add it to the appropriate provider's JSON file. For example, to add a new OpenAI model, you would add it to the `openai.json` file.

Here's an example of adding a new model:

```json
{
  "number": "10",
  "modelName": "gpt-5",
  "name": "GPT-5",
  "type": "Text Generation",
  "inputPricePer1KTokens": 0.001,
  "outputPricePer1KTokens": 0.002,
  "description": "The latest and most powerful GPT model.",
  "contextWindows": "256k Tokens",
  "recommended": true,
  "commercial": true,
  "pricey": true,
  "output": "32768 Tokens",
  "comments": "Most powerful model available.",
  "companyModelName": "Openai : GPT-5",
  "promptTemplate": "<|start_header_id|>user<|end_header_id|>\n\n%1<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n%2<|eot_id|>",
  "systemPrompt": ""
}
```

## Adding New Providers

To add a new provider, you need to:

1. Create a new JSON file in the `providers/json` directory with the provider's models.
2. Update the `provider_map` in the `load_provider_models` function in the `model_info` module.
3. Create a new provider implementation in the `providers` directory.
4. Update the `PROVIDER_FACTORIES` in the `factory.py` file in the `providers` directory.

Here's an example of adding a new provider:

1. Create a new JSON file `providers/json/newprovider.json`:

```json
[
  {
    "number": "1",
    "modelName": "new-model",
    "name": "New Model",
    "type": "Text Generation",
    "inputPricePer1KTokens": 0.0001,
    "outputPricePer1KTokens": 0.0002,
    "description": "A new model from a new provider.",
    "contextWindows": "32k Tokens",
    "recommended": true,
    "commercial": false,
    "pricey": false,
    "output": "4096 Tokens",
    "comments": "New provider's flagship model.",
    "companyModelName": "NewProvider : New Model",
    "promptTemplate": "",
    "systemPrompt": ""
  }
]
```

2. Update the `provider_map` in the `load_provider_models` function:

```python
# Map provider IDs to JSON file names
provider_map = {
    "openai": "openai.json",
    "anthropic": "claude.json",
    "cohere": "cohere.json",
    "google": "google.json",
    "mistral": "mistral.json",
    "meta": "meta.json",
    "nvidia": "nvidia.json",
    "databricks": "databricks.json",
    "ai21labs": "ai21labs.json",
    "qwen": "qwen.json",
    "deepseek": "deepseek.json",
    "newprovider": "newprovider.json",  # Add the new provider
}
```

3. Create a new provider implementation `providers/newprovider_provider.py`.

4. Update the `PROVIDER_FACTORIES` in the `factory.py` file:

```python
# Provider factory mapping
PROVIDER_FACTORIES = {
    "openai": get_openai_provider,
    "anthropic": get_anthropic_provider,
    "cohere": get_cohere_provider,
    "google": get_google_provider,
    "mistral": get_mistral_provider,
    "newprovider": get_newprovider_provider,  # Add the new provider
}
```

## Best Practices

- Keep model information up to date with the latest pricing and capabilities.
- Use the model information system to provide users with information about available models.
- Use the model information system to calculate costs accurately.
- Consider adding additional metadata to the model information to help users choose the right model for their needs.
