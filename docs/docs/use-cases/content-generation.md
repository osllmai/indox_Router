# Content Generation with IndoxRouter

IndoxRouter provides access to powerful language models that can be used for a wide range of content generation tasks. This guide demonstrates various content generation use cases and how to implement them.

## Text Generation Basics

At its core, content generation involves prompting a language model to produce text that meets specific requirements. Here's a simple example:

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

# Generate a short blog post
response = client.chat(
    messages=[
        {"role": "system", "content": "You are a professional blog writer with expertise in technology."},
        {"role": "user", "content": "Write a 300-word blog post about the impact of AI on content creation."}
    ],
    model="openai/gpt-4o"
)

blog_post = response["data"]
print(blog_post)
```

## Creative Writing

Language models can generate creative content like stories, poems, and scripts:

```python
# Generate a short story
story_response = client.chat(
    messages=[
        {"role": "system", "content": "You are a creative fiction writer with a talent for engaging narratives."},
        {"role": "user", "content": (
            "Write a short story (around 500 words) about a scientist who discovers "
            "a way to communicate with plants. The story should have a surprising twist ending."
        )}
    ],
    model="anthropic/claude-3-opus-20240229",
    temperature=0.8  # Higher temperature for more creativity
)

story = story_response["data"]
```

## SEO Content Creation

Generate SEO-optimized content for websites and marketing:

```python
# Generate SEO-optimized article
seo_response = client.chat(
    messages=[
        {"role": "system", "content": (
            "You are an SEO content expert who writes engaging, informative content "
            "that ranks well in search engines. Include appropriate headings (H2, H3), "
            "bullet points where relevant, and a conclusion."
        )},
        {"role": "user", "content": (
            "Write a comprehensive SEO article (800-1000 words) about 'Best Practices for Machine Learning Deployment' "
            "targeting developers and data scientists. Include these keywords naturally: machine learning operations, "
            "MLOps, model monitoring, deployment pipeline, and containerization."
        )}
    ],
    model="openai/gpt-4o",
    temperature=0.7
)

seo_article = seo_response["data"]
```

## Product Descriptions

Create compelling product descriptions for e-commerce:

```python
def generate_product_description(product_name, features, target_audience, word_count=200):
    """Generate a product description based on product details."""
    features_text = "\n".join([f"- {feature}" for feature in features])

    prompt = f"""
    Product: {product_name}
    Features:
    {features_text}
    Target Audience: {target_audience}
    Word Count: {word_count}

    Write a compelling product description that highlights the features and benefits.
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a marketing copywriter who creates compelling product descriptions."},
            {"role": "user", "content": prompt}
        ],
        model="mistral/mistral-large-latest",
        temperature=0.7
    )

    return response["data"]

# Example usage
product_description = generate_product_description(
    product_name="EcoCharge Solar Power Bank",
    features=[
        "25,000mAh capacity",
        "Solar charging capability",
        "Fast-charging USB-C port",
        "Built-in LED flashlight",
        "Waterproof (IP67 rating)"
    ],
    target_audience="Outdoor enthusiasts and travelers",
    word_count=150
)
```

## Email Marketing Campaigns

Generate email marketing content with different styles:

```python
def generate_email_campaign(campaign_type, product_info, audience, call_to_action):
    """Generate email marketing content based on campaign type."""

    campaign_prompts = {
        "welcome": "Write a friendly welcome email for new subscribers.",
        "promotional": "Write a promotional email announcing a new product or special offer.",
        "newsletter": "Write a newsletter email with updates and valuable content.",
        "abandonment": "Write a cart abandonment email to remind customers of items left in their cart.",
        "follow_up": "Write a follow-up email after a purchase to thank the customer and suggest next steps."
    }

    if campaign_type not in campaign_prompts:
        raise ValueError(f"Campaign type must be one of: {', '.join(campaign_prompts.keys())}")

    prompt = f"""
    Campaign Type: {campaign_type} email
    Product/Service Information: {product_info}
    Target Audience: {audience}
    Call to Action: {call_to_action}

    {campaign_prompts[campaign_type]}
    Include a subject line, greeting, body, and sign-off.
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": "You are an email marketing specialist who writes compelling emails that convert."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-4o-mini",
        temperature=0.7
    )

    return response["data"]

# Example usage
welcome_email = generate_email_campaign(
    campaign_type="welcome",
    product_info="TechNest - A productivity app for managing tasks, notes, and projects",
    audience="New app subscribers, primarily professionals aged 25-45",
    call_to_action="Download the app and complete the onboarding tour"
)
```

## Social Media Content

Generate content for different social media platforms:

```python
def generate_social_media_post(platform, topic, tone, hashtags=None, include_emoji=True):
    """Generate a social media post tailored to a specific platform."""

    platform_guidelines = {
        "twitter": "Write a concise post under 280 characters.",
        "instagram": "Write an engaging caption that works well with a visual. Include line breaks for readability.",
        "linkedin": "Write a professional post that provides value to a business audience. Can be longer format.",
        "facebook": "Write a conversational post that encourages engagement and interaction.",
        "tiktok": "Write a catchy, trend-aware caption that would work well with a short video."
    }

    if platform not in platform_guidelines:
        raise ValueError(f"Platform must be one of: {', '.join(platform_guidelines.keys())}")

    hashtag_text = ""
    if hashtags:
        hashtag_text = f"\nSuggested hashtags: {', '.join(hashtags)}"

    emoji_instruction = "Include appropriate emojis to increase engagement." if include_emoji else "Don't use emojis."

    prompt = f"""
    Platform: {platform}
    Topic: {topic}
    Tone: {tone}
    {hashtag_text}

    {platform_guidelines[platform]}
    {emoji_instruction}
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a social media content creator who crafts engaging posts."},
            {"role": "user", "content": prompt}
        ],
        model="anthropic/claude-3-haiku-20240307",
        temperature=0.7
    )

    return response["data"]

# Example usage
linkedin_post = generate_social_media_post(
    platform="linkedin",
    topic="How AI is transforming data analysis in finance",
    tone="professional and informative",
    hashtags=["AIinFinance", "DataAnalytics", "FinTech", "MachineLearning"],
    include_emoji=True
)
```

## Content Repurposing

Take existing content and repurpose it for different formats:

```python
def repurpose_content(original_content, original_format, target_format, target_length=None):
    """Repurpose content from one format to another."""

    length_instruction = f"The target length should be approximately {target_length} words." if target_length else ""

    prompt = f"""
    Original Content ({original_format}):

    {original_content}

    Please repurpose this content into a {target_format} format.
    {length_instruction}
    Maintain the key points and message while adapting to the new format's requirements.
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a content repurposing specialist who can transform content between different formats while preserving the core message."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-4o",
        temperature=0.7
    )

    return response["data"]

# Example usage
blog_post = """
# The Future of Remote Work
Remote work has transformed how businesses operate in the digital age. Since the COVID-19 pandemic, companies have discovered both challenges and benefits of distributed teams. Studies show productivity often increases, while office costs decrease. However, maintaining company culture and collaboration requires intentional strategies and tools. The future likely holds a hybrid model, combining in-person collaboration with remote flexibility.
"""

# Repurpose to different formats
twitter_thread = repurpose_content(blog_post, "blog post", "Twitter thread (5-7 tweets)")
video_script = repurpose_content(blog_post, "blog post", "video script", 300)
newsletter = repurpose_content(blog_post, "blog post", "email newsletter", 250)
```

## Data-Driven Content

Generate content based on data and analysis:

```python
def generate_data_report(data_summary, key_findings, audience, report_type="executive_summary"):
    """Generate a data-driven report based on findings."""

    report_types = {
        "executive_summary": "Write a concise executive summary highlighting the most important insights.",
        "detailed_analysis": "Write a detailed analysis explaining all findings and their implications.",
        "recommendation": "Write recommendations based on the data findings.",
        "press_release": "Write a press release announcing the key findings."
    }

    if report_type not in report_types:
        raise ValueError(f"Report type must be one of: {', '.join(report_types.keys())}")

    prompt = f"""
    Data Summary: {data_summary}
    Key Findings:
    {key_findings}
    Target Audience: {audience}

    {report_types[report_type]}
    Use a professional tone and focus on actionable insights.
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a data analyst who creates clear, insightful reports from complex data."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-4o",
        temperature=0.3  # Lower temperature for more factual content
    )

    return response["data"]

# Example usage
executive_summary = generate_data_report(
    data_summary="Survey of 1,000 consumers about shopping habits",
    key_findings="""
    - 67% of consumers prefer shopping online for electronics
    - 82% read at least 3 reviews before making purchases over $100
    - Mobile shopping increased by 34% compared to last year
    - 45% of customers abandon carts due to high shipping costs
    - Loyalty programs influence 58% of repeat purchases
    """,
    audience="E-commerce business executives",
    report_type="executive_summary"
)
```

## Content Translation and Localization

Translate and adapt content for different regions:

```python
def translate_and_localize(content, source_language, target_language, target_region=None, content_type="general"):
    """Translate and localize content for a specific language and region."""

    region_instruction = f"Adapt for {target_region} region specifically." if target_region else ""

    content_type_instructions = {
        "general": "Translate the content while maintaining the original meaning.",
        "marketing": "Translate and adapt marketing content to resonate with the target culture.",
        "technical": "Translate technical content with precision, maintaining all technical details.",
        "legal": "Translate legal content accurately, using appropriate legal terminology."
    }

    if content_type not in content_type_instructions:
        raise ValueError(f"Content type must be one of: {', '.join(content_type_instructions.keys())}")

    prompt = f"""
    Original Content ({source_language}):

    {content}

    Please translate this content into {target_language}.
    {region_instruction}

    Content Type: {content_type}
    {content_type_instructions[content_type]}

    Note any cultural adaptations made in your translation.
    """

    response = client.chat(
        messages=[
            {"role": "system", "content": f"You are a professional translator fluent in {source_language} and {target_language} with expertise in cultural localization."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-4o",
        temperature=0.4
    )

    return response["data"]

# Example usage
english_content = """
Our Premium Membership gives you access to all courses, workshops, and resources.
Sign up today and get a 20% discount for the first three months!
"""

spanish_translation = translate_and_localize(
    content=english_content,
    source_language="English",
    target_language="Spanish",
    target_region="Mexico",
    content_type="marketing"
)
```

## Best Practices for Content Generation

1. **Iterative Refinement**: Generate a draft, then refine it with additional prompts
2. **Specific Instructions**: Provide clear, detailed instructions about tone, style, and format
3. **Model Selection**: Choose the appropriate model based on the content complexity
4. **Temperature Control**: Use higher temperature for creative content, lower for factual content
5. **Content Verification**: Always review AI-generated content for accuracy and appropriateness
6. **A/B Testing**: Generate multiple versions and test their effectiveness
7. **Human Touch**: Add human editing to enhance and personalize the content

_Last updated: Nov 11, 2025_