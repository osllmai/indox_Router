# Rate Limits

IndoxRouter implements a three-tier rate limiting system to ensure fair usage and optimal performance. Understanding these limits helps you optimize your application's AI usage.

## Rate Limit Tiers

IndoxRouter has three subscription tiers with different rate limits:

```python
# Rate limits by tier
RATE_LIMITS = {
    "free": {
        "requests_per_minute": 10,
        "tokens_per_hour": 10000
    },
    "standard": {
        "requests_per_minute": 60,
        "tokens_per_hour": 100000
    },
    "enterprise": {
        "requests_per_minute": 500,
        "tokens_per_hour": 1000000
    }
}
```

### Tier Comparison

| Tier           | Requests/Minute | Tokens/Hour | Best For                              |
| -------------- | --------------- | ----------- | ------------------------------------- |
| **Free**       | 10              | 10,000      | Testing, prototyping, learning        |
| **Standard**   | 60              | 100,000     | Production apps, small businesses     |
| **Enterprise** | 500             | 1,000,000   | High-volume applications, enterprises |

### What Counts Toward Limits

#### Request Limits

Every API call counts as one request:

- `client.chat()` = 1 request
- `client.completions()` = 1 request
- `client.embeddings()` = 1 request
- `client.images()` = 1 request
- `client.models()` = 1 request (but doesn't count toward token limits)

#### Token Limits

Tokens are counted for text-based operations:

- **Chat & Completions**: Input tokens + output tokens
- **Embeddings**: Input tokens only
- **Images**: No tokens counted (separate limits may apply)
- **Models/Info calls**: No tokens counted

## Rate Limit Headers

Every response includes rate limit information in the headers and response:

```python
response = client.chat(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)

# Rate limit info is included in response metadata
print(f"Request ID: {response['request_id']}")
print(f"Duration: {response['duration_ms']}ms")

# Check your current usage
usage = client.get_usage()
print(f"Remaining credits: ${usage['remaining_credits']}")
```

## Handling Rate Limits

### Rate Limit Errors

When you exceed rate limits, you'll receive an error response:

```python
{
    'success': False,
    'error': 'RateLimitError',
    'message': 'Rate limit exceeded: 10 requests per minute',
    'status_code': 429,
    'request_id': 'req_rate_limit_123',
    'details': {
        'limit_type': 'requests_per_minute',
        'limit': 10,
        'reset_time': '2025-05-19T10:35:00Z',
        'retry_after': 45  # seconds
    }
}
```

### Error Handling Example

```python
from indoxrouter import Client, RateLimitError
import time

client = Client(api_key="your_api_key")

def make_request_with_retry(messages, model, max_retries=3):
    """Make request with automatic retry on rate limit."""

    for attempt in range(max_retries):
        try:
            response = client.chat(messages=messages, model=model)

            if response['success']:
                return response
            else:
                # Handle other errors
                print(f"Request failed: {response['message']}")
                return response

        except RateLimitError as e:
            print(f"Rate limit hit (attempt {attempt + 1}/{max_retries})")

            if attempt < max_retries - 1:
                # Extract retry delay from error details
                retry_after = getattr(e, 'retry_after', 60)
                print(f"Waiting {retry_after} seconds before retry...")
                time.sleep(retry_after)
            else:
                print("Max retries exceeded")
                raise

        except Exception as e:
            print(f"Request failed with error: {e}")
            raise

    return None

# Usage
response = make_request_with_retry(
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)
```

## Rate Limit Management

### Request Batching

For high-volume applications, batch your requests efficiently:

```python
import time
from datetime import datetime, timedelta

class RateLimitManager:
    """Manage requests within rate limits."""

    def __init__(self, client, requests_per_minute=60, tokens_per_hour=100000):
        self.client = client
        self.requests_per_minute = requests_per_minute
        self.tokens_per_hour = tokens_per_hour

        # Tracking
        self.request_timestamps = []
        self.token_usage_hourly = []

    def can_make_request(self, estimated_tokens=100):
        """Check if we can make a request within limits."""
        now = datetime.now()

        # Clean old request timestamps (older than 1 minute)
        minute_ago = now - timedelta(minutes=1)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]

        # Clean old token usage (older than 1 hour)
        hour_ago = now - timedelta(hours=1)
        self.token_usage_hourly = [(ts, tokens) for ts, tokens in self.token_usage_hourly if ts > hour_ago]

        # Check request limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            return False, "Request rate limit would be exceeded"

        # Check token limit
        current_hourly_tokens = sum(tokens for _, tokens in self.token_usage_hourly)
        if current_hourly_tokens + estimated_tokens > self.tokens_per_hour:
            return False, "Token rate limit would be exceeded"

        return True, "OK"

    def make_request(self, request_func, estimated_tokens=100, **kwargs):
        """Make request with rate limit checking."""
        can_request, reason = self.can_make_request(estimated_tokens)

        if not can_request:
            # Calculate wait time
            if "request" in reason.lower():
                wait_time = 60 - (datetime.now() - min(self.request_timestamps)).total_seconds()
            else:  # token limit
                wait_time = 3600 - (datetime.now() - min(ts for ts, _ in self.token_usage_hourly)).total_seconds()

            print(f"Rate limit hit: {reason}")
            print(f"Estimated wait time: {wait_time:.0f} seconds")
            return None

        # Make the request
        try:
            response = request_func(**kwargs)

            # Track the request
            now = datetime.now()
            self.request_timestamps.append(now)

            # Track token usage if successful
            if response.get('success') and 'usage' in response:
                actual_tokens = response['usage']['tokens_total']
                self.token_usage_hourly.append((now, actual_tokens))

            return response

        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def wait_for_rate_limit_reset(self):
        """Wait for rate limits to reset."""
        now = datetime.now()

        # Find when we can make the next request
        if self.request_timestamps:
            next_request_time = min(self.request_timestamps) + timedelta(minutes=1)
            if next_request_time > now:
                wait_seconds = (next_request_time - now).total_seconds()
                print(f"Waiting {wait_seconds:.0f} seconds for request limit reset...")
                time.sleep(wait_seconds)

        # Find when we have token capacity
        if self.token_usage_hourly:
            next_token_time = min(ts for ts, _ in self.token_usage_hourly) + timedelta(hours=1)
            if next_token_time > now:
                wait_seconds = (next_token_time - now).total_seconds()
                print(f"Waiting {wait_seconds:.0f} seconds for token limit reset...")
                time.sleep(wait_seconds)

# Usage example
rate_manager = RateLimitManager(client, requests_per_minute=60, tokens_per_hour=100000)

# Make a managed request
response = rate_manager.make_request(
    client.chat,
    estimated_tokens=150,
    messages=[{"role": "user", "content": "Hello"}],
    model="openai/gpt-4o-mini"
)

if response:
    print(f"Response: {response['data']}")
    print(f"Actual tokens used: {response['usage']['tokens_total']}")
```

### Batch Processing

For processing multiple items efficiently:

```python
def process_batch_with_rate_limits(client, items, batch_size=10):
    """Process items in batches respecting rate limits."""

    rate_manager = RateLimitManager(client)
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = []

        print(f"Processing batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}")

        for item in batch:
            # Check if we can make request
            can_request, reason = rate_manager.can_make_request(estimated_tokens=100)

            if not can_request:
                print(f"Rate limit hit, waiting...")
                rate_manager.wait_for_rate_limit_reset()

            # Make the request
            response = rate_manager.make_request(
                client.chat,
                estimated_tokens=100,
                messages=[{"role": "user", "content": f"Process this item: {item}"}],
                model="openai/gpt-4o-mini"
            )

            if response and response['success']:
                batch_results.append({
                    'item': item,
                    'result': response['data'],
                    'cost': response['usage']['cost'],
                    'tokens': response['usage']['tokens_total']
                })
            else:
                batch_results.append({
                    'item': item,
                    'result': None,
                    'error': response.get('message', 'Unknown error') if response else 'Request failed'
                })

        results.extend(batch_results)

        # Brief pause between batches
        time.sleep(1)

    return results

# Process a list of items
items_to_process = [
    "Translate this to French: Hello world",
    "Summarize: The quick brown fox...",
    "Generate a haiku about rain",
    # ... more items
]

results = process_batch_with_rate_limits(client, items_to_process)

# Analyze results
successful = [r for r in results if r['result'] is not None]
failed = [r for r in results if r['result'] is None]

print(f"Successfully processed: {len(successful)}/{len(results)}")
print(f"Total cost: ${sum(r.get('cost', 0) for r in successful):.4f}")
print(f"Total tokens: {sum(r.get('tokens', 0) for r in successful):,}")
```

## Optimization Strategies

### 1. Token-Efficient Prompts

Reduce token usage to stay within hourly limits:

```python
def optimize_prompt_tokens(original_prompt, target_tokens=100):
    """Optimize prompts to use fewer tokens."""

    # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
    estimated_tokens = len(original_prompt) // 4

    if estimated_tokens <= target_tokens:
        return original_prompt

    # Optimization strategies
    optimized_prompt = original_prompt

    # Remove extra whitespace
    optimized_prompt = ' '.join(optimized_prompt.split())

    # Use abbreviations
    replacements = {
        'please': 'pls',
        'because': 'bc',
        'without': 'w/o',
        'with': 'w/',
        'and': '&',
        'you are': "you're",
        'do not': "don't",
        'cannot': "can't"
    }

    for old, new in replacements.items():
        optimized_prompt = optimized_prompt.replace(old, new)

    # If still too long, truncate with ellipsis
    target_chars = target_tokens * 4
    if len(optimized_prompt) > target_chars:
        optimized_prompt = optimized_prompt[:target_chars-3] + "..."

    return optimized_prompt

# Example usage
long_prompt = """
Please analyze this text very carefully and provide a comprehensive summary
that includes all the key points, main arguments, supporting evidence, and
conclusions. Make sure to maintain the original tone and style.
"""

optimized = optimize_prompt_tokens(long_prompt, target_tokens=50)
print(f"Original: {len(long_prompt)} chars")
print(f"Optimized: {len(optimized)} chars")
print(f"Optimized prompt: {optimized}")
```

### 2. Smart Model Selection

Choose models based on rate limits and requirements:

```python
def select_optimal_model(task_complexity, urgency="normal", tier="standard"):
    """Select the best model based on constraints."""

    # Model efficiency ratings (cost per token)
    model_efficiency = {
        "openai/gpt-3.5-turbo": {"cost_per_token": 0.000001, "quality": 7},
        "openai/gpt-4o-mini": {"cost_per_token": 0.000002, "quality": 8},
        "openai/gpt-4o": {"cost_per_token": 0.000030, "quality": 10},
        "anthropic/claude-3-haiku-20240307": {"cost_per_token": 0.000002, "quality": 8},
        "anthropic/claude-3-sonnet-20240229": {"cost_per_token": 0.000008, "quality": 9},
        "anthropic/claude-3-opus-20240229": {"cost_per_token": 0.000020, "quality": 10},
        "deepseek/deepseek-chat": {"cost_per_token": 0.0000005, "quality": 7}
    }

    # Filter models based on tier token limits
    tier_limits = {
        "free": 10000,      # 10K tokens/hour
        "standard": 100000,  # 100K tokens/hour
        "enterprise": 1000000 # 1M tokens/hour
    }

    hourly_limit = tier_limits.get(tier, 100000)

    if task_complexity == "simple" and hourly_limit < 50000:
        # Use most efficient models for high-volume, low-complexity tasks
        recommended = ["deepseek/deepseek-chat", "openai/gpt-3.5-turbo"]
    elif task_complexity == "moderate":
        recommended = ["openai/gpt-4o-mini", "anthropic/claude-3-haiku-20240307"]
    else:  # complex
        if urgency == "high" or hourly_limit > 500000:
            recommended = ["openai/gpt-4o", "anthropic/claude-3-opus-20240229"]
        else:
            recommended = ["anthropic/claude-3-sonnet-20240229", "openai/gpt-4o-mini"]

    # Return best option with reasoning
    best_model = recommended[0]
    model_info = model_efficiency[best_model]

    return {
        'model': best_model,
        'reasoning': f"Selected for {task_complexity} task with {tier} tier limits",
        'cost_per_token': model_info['cost_per_token'],
        'quality_rating': model_info['quality'],
        'alternatives': recommended[1:] if len(recommended) > 1 else []
    }

# Example usage
selection = select_optimal_model("simple", "normal", "standard")
print(f"Recommended model: {selection['model']}")
print(f"Reasoning: {selection['reasoning']}")
print(f"Cost per token: ${selection['cost_per_token']:.7f}")
```

### 3. Request Scheduling

Distribute requests to avoid rate limit peaks:

```python
import time
from datetime import datetime, timedelta
import random

class RequestScheduler:
    """Schedule requests to optimize rate limit usage."""

    def __init__(self, client, requests_per_minute=60):
        self.client = client
        self.requests_per_minute = requests_per_minute
        self.request_queue = []

    def add_request(self, request_func, priority=1, **kwargs):
        """Add request to queue with priority."""
        self.request_queue.append({
            'func': request_func,
            'kwargs': kwargs,
            'priority': priority,
            'added_at': datetime.now()
        })

        # Sort by priority (higher number = higher priority)
        self.request_queue.sort(key=lambda x: x['priority'], reverse=True)

    def process_queue(self, max_concurrent=5):
        """Process queued requests respecting rate limits."""

        # Calculate optimal delay between requests
        min_delay = 60 / self.requests_per_minute  # seconds between requests

        results = []
        processed = 0

        while self.request_queue and processed < max_concurrent:
            request = self.request_queue.pop(0)

            try:
                # Add small random delay to avoid synchronized requests
                jitter = random.uniform(0, min_delay * 0.1)
                time.sleep(min_delay + jitter)

                print(f"Processing request {processed + 1}/{min(len(self.request_queue) + 1, max_concurrent)}")

                response = request['func'](**request['kwargs'])
                results.append({
                    'request': request,
                    'response': response,
                    'processed_at': datetime.now()
                })

                processed += 1

            except Exception as e:
                print(f"Request failed: {e}")
                results.append({
                    'request': request,
                    'response': None,
                    'error': str(e),
                    'processed_at': datetime.now()
                })

        return results

# Usage example
scheduler = RequestScheduler(client, requests_per_minute=60)

# Add requests with different priorities
scheduler.add_request(
    client.chat,
    priority=3,  # High priority
    messages=[{"role": "user", "content": "Urgent: Translate 'Hello' to French"}],
    model="openai/gpt-4o-mini"
)

scheduler.add_request(
    client.chat,
    priority=1,  # Low priority
    messages=[{"role": "user", "content": "Generate a fun fact about cats"}],
    model="openai/gpt-3.5-turbo"
)

scheduler.add_request(
    client.chat,
    priority=2,  # Medium priority
    messages=[{"role": "user", "content": "Summarize the latest news"}],
    model="openai/gpt-4o-mini"
)

# Process the queue
results = scheduler.process_queue(max_concurrent=3)

print(f"Processed {len(results)} requests")
for i, result in enumerate(results, 1):
    if result['response'] and result['response']['success']:
        print(f"{i}. Success: {result['response']['data'][:50]}...")
    else:
        print(f"{i}. Failed: {result.get('error', 'Unknown error')}")
```

## Monitoring Rate Limits

### Real-time Rate Limit Tracking

```python
class RateLimitMonitor:
    """Monitor rate limit usage in real-time."""

    def __init__(self, requests_per_minute=60, tokens_per_hour=100000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_hour = tokens_per_hour
        self.request_timestamps = []
        self.token_usage = []

    def log_request(self, response):
        """Log a request and its token usage."""
        now = datetime.now()
        self.request_timestamps.append(now)

        if response and response.get('success') and 'usage' in response:
            tokens = response['usage']['tokens_total']
            self.token_usage.append((now, tokens))

    def get_current_usage(self):
        """Get current rate limit usage."""
        now = datetime.now()

        # Clean old data
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]
        self.token_usage = [(ts, tokens) for ts, tokens in self.token_usage if ts > hour_ago]

        # Calculate current usage
        current_requests = len(self.request_timestamps)
        current_tokens = sum(tokens for _, tokens in self.token_usage)

        return {
            'requests': {
                'current': current_requests,
                'limit': self.requests_per_minute,
                'percentage': (current_requests / self.requests_per_minute * 100) if self.requests_per_minute > 0 else 0,
                'remaining': max(0, self.requests_per_minute - current_requests)
            },
            'tokens': {
                'current': current_tokens,
                'limit': self.tokens_per_hour,
                'percentage': (current_tokens / self.tokens_per_hour * 100) if self.tokens_per_hour > 0 else 0,
                'remaining': max(0, self.tokens_per_hour - current_tokens)
            }
        }

    def print_status(self):
        """Print current rate limit status."""
        usage = self.get_current_usage()

        print(f"📊 Rate Limit Status")
        print(f"   Requests: {usage['requests']['current']}/{usage['requests']['limit']} ({usage['requests']['percentage']:.1f}%)")
        print(f"   Tokens: {usage['tokens']['current']:,}/{usage['tokens']['limit']:,} ({usage['tokens']['percentage']:.1f}%)")

        if usage['requests']['percentage'] > 80:
            print(f"   ⚠️  High request usage")
        if usage['tokens']['percentage'] > 80:
            print(f"   ⚠️  High token usage")

# Usage
monitor = RateLimitMonitor(requests_per_minute=60, tokens_per_hour=100000)

# Make some requests
for i in range(5):
    response = client.chat(
        messages=[{"role": "user", "content": f"Request {i+1}"}],
        model="openai/gpt-4o-mini"
    )
    monitor.log_request(response)

    # Show status every few requests
    if (i + 1) % 2 == 0:
        monitor.print_status()
        print()
```

## Best Practices

### 1. Respect Rate Limits

```python
# Always implement retry logic with exponential backoff
def make_request_with_backoff(client, request_func, max_retries=3, **kwargs):
    """Make request with exponential backoff on rate limits."""

    for attempt in range(max_retries):
        try:
            response = request_func(**kwargs)
            return response

        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 60  # Exponential backoff: 1min, 2min, 4min
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

    return None
```

### 2. Optimize Token Usage

```python
# Use efficient prompting techniques
def create_efficient_prompt(task, context="", max_tokens=100):
    """Create token-efficient prompts."""

    # Use concise language
    efficient_prompt = f"Task: {task}"

    if context:
        # Limit context to essential information
        context_limit = max_tokens // 2
        if len(context) > context_limit * 4:  # Rough token estimation
            context = context[:context_limit * 4] + "..."
        efficient_prompt += f"\nContext: {context}"

    efficient_prompt += "\nResponse:"

    return efficient_prompt

# Example
task = "Summarize the main points"
context = "Long document text here..."
prompt = create_efficient_prompt(task, context, max_tokens=150)
```

### 3. Monitor and Alert

```python
# Set up monitoring for your application
def setup_rate_limit_alerts(client, alert_threshold=0.8):
    """Set up alerts for rate limit usage."""

    monitor = RateLimitMonitor()

    def check_and_alert():
        usage = monitor.get_current_usage()

        if usage['requests']['percentage'] > alert_threshold * 100:
            print(f"🚨 Request rate limit alert: {usage['requests']['percentage']:.1f}% used")

        if usage['tokens']['percentage'] > alert_threshold * 100:
            print(f"🚨 Token rate limit alert: {usage['tokens']['percentage']:.1f}% used")

    return monitor, check_and_alert

# Use monitoring
monitor, alert_check = setup_rate_limit_alerts(client)

# In your application loop
response = client.chat(messages=[...], model="openai/gpt-4o-mini")
monitor.log_request(response)
alert_check()
```

_Last updated: Nov 08, 2025_