# Usage Tracking

indoxhub provides comprehensive usage tracking to help you monitor your API consumption, costs, and performance metrics.

## Getting Usage Statistics

Use the `get_usage()` method to retrieve detailed usage information:

```python
from indoxhub import indoxhub

client = indoxhub(api_key="your-api-key")

# Get current usage statistics
usage_stats = client.get_usage()
print(usage_stats)
```

## Usage Response Format

The `get_usage()` method returns detailed statistics including:

```python
{
    "total_requests": 1250,
    "total_tokens": 45000,
    "total_cost": 12.50,
    "current_period": {
        "requests": 150,
        "tokens": 5500,
        "cost": 1.75,
        "period_start": "2024-01-01T00:00:00Z",
        "period_end": "2024-01-31T23:59:59Z"
    },
    "by_provider": {
        "openai": {
            "requests": 800,
            "tokens": 28000,
            "cost": 8.40
        },
        "anthropic": {
            "requests": 300,
            "tokens": 12000,
            "cost": 2.88
        },
        "google": {
            "requests": 150,
            "tokens": 5000,
            "cost": 1.22
        }
    },
    "by_model": {
        "gpt-4": {
            "requests": 400,
            "tokens": 15000,
            "cost": 4.50
        },
        "claude-3-sonnet": {
            "requests": 300,
            "tokens": 12000,
            "cost": 2.88
        },
        "gemini-pro": {
            "requests": 150,
            "tokens": 5000,
            "cost": 1.22
        }
    }
}
```

## Real-time Usage in Responses

Every API response includes detailed usage information:

### Chat Completion Usage

```python
response = client.chat_completions(
    provider="openai",
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Access usage information
usage = response.usage
print(f"Prompt tokens: {usage.prompt_tokens}")
print(f"Completion tokens: {usage.completion_tokens}")
print(f"Total tokens: {usage.total_tokens}")
print(f"Cost: ${usage.cost_breakdown.total_cost}")
```

### Detailed Usage Fields

Each response includes comprehensive usage tracking:

- **`prompt_tokens`**: Tokens used in the input
- **`completion_tokens`**: Tokens generated in the response
- **`total_tokens`**: Sum of prompt and completion tokens
- **`cache_read_tokens`**: Tokens read from cache (if applicable)
- **`cache_write_tokens`**: Tokens written to cache (if applicable)
- **`reasoning_tokens`**: Tokens used for reasoning (for reasoning models)
- **`web_search_count`**: Number of web searches performed
- **`request_count`**: Number of API requests made
- **`cost_breakdown`**: Detailed cost information

### Cost Breakdown

The `cost_breakdown` object provides detailed pricing information:

```python
{
    "prompt_cost": 0.015,
    "completion_cost": 0.030,
    "cache_read_cost": 0.0015,
    "cache_write_cost": 0.0075,
    "reasoning_cost": 0.240,
    "web_search_cost": 0.001,
    "total_cost": 0.2935
}
```

## Monitoring Best Practices

### 1. Regular Usage Checks

```python
# Check usage before making expensive requests
usage = client.get_usage()
if usage["current_period"]["cost"] > 50.0:
    print("Warning: High usage this period")
```

### 2. Provider Cost Optimization

```python
# Compare costs across providers
usage = client.get_usage()
for provider, stats in usage["by_provider"].items():
    cost_per_token = stats["cost"] / stats["tokens"]
    print(f"{provider}: ${cost_per_token:.6f} per token")
```

### 3. Model Performance Tracking

```python
# Track model efficiency
usage = client.get_usage()
for model, stats in usage["by_model"].items():
    avg_tokens_per_request = stats["tokens"] / stats["requests"]
    print(f"{model}: {avg_tokens_per_request:.1f} tokens per request")
```

## Rate Limit Monitoring

Usage tracking also helps monitor rate limit consumption:

```python
# Check current rate limit status
usage = client.get_usage()
current_requests = usage["current_period"]["requests"]
print(f"Requests this period: {current_requests}")

# Rate limits vary by tier:
# - Free: 10 requests/minute, 10K tokens/hour
# - Standard: 60 requests/minute, 100K tokens/hour
# - Enterprise: 500 requests/minute, 1M tokens/hour
```

## Export Usage Data

For detailed analysis, you can export usage data:

```python
import json
from datetime import datetime

# Get usage data
usage = client.get_usage()

# Save to file with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"usage_report_{timestamp}.json"

with open(filename, 'w') as f:
    json.dump(usage, f, indent=2)

print(f"Usage report saved to {filename}")
```

## Integration with Analytics

Usage data can be integrated with analytics platforms:

```python
# Example: Send to analytics service
def track_usage_metrics(usage_data):
    metrics = {
        'total_requests': usage_data['total_requests'],
        'total_cost': usage_data['total_cost'],
        'avg_cost_per_request': usage_data['total_cost'] / usage_data['total_requests']
    }

    # Send to your analytics platform
    # analytics_client.track('api_usage', metrics)

track_usage_metrics(client.get_usage())
```

_Last updated: Nov 16, 2025_