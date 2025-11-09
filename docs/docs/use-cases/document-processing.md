# Document Processing with IndoxRouter

IndoxRouter provides powerful capabilities for processing and analyzing documents using various language models. This guide covers common document processing tasks and patterns.

## Text Extraction and Summarization

### Document Summarization

```python
from indoxrouter import Client

client = Client(api_key="your_api_key")

def summarize_document(text, max_length=200):
    """Summarize a long document into key points."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Summarize the following document in {max_length} words or less. Focus on the main points and key information."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini",
        max_tokens=max_length * 2  # Rough estimate for token count
    )

    return response["data"]

# Example usage
document = """
Your long document text here...
This could be a research paper, article, report, etc.
"""

summary = summarize_document(document)
print("Summary:", summary)
```

### Extractive vs Abstractive Summarization

```python
def extractive_summary(text, num_sentences=3):
    """Extract key sentences from the document."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Extract the {num_sentences} most important sentences from the following text. Return only the sentences, separated by newlines."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

def abstractive_summary(text, style="professional"):
    """Generate a new summary in the specified style."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Create a {style} summary of the following document. Write it in your own words, capturing the essence and main ideas."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

## Document Classification

### Topic Classification

```python
def classify_document(text, categories):
    """Classify a document into predefined categories."""

    categories_str = ", ".join(categories)

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Classify the following document into one of these categories: {categories_str}. Respond with only the category name and a confidence score (0-1)."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example usage
categories = ["Technology", "Finance", "Healthcare", "Education", "Sports"]
classification = classify_document(document, categories)
print("Classification:", classification)
```

### Sentiment Analysis

```python
def analyze_sentiment(text):
    """Analyze the sentiment of a document."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": "Analyze the sentiment of the following text. Provide: 1) Overall sentiment (positive/negative/neutral), 2) Confidence score (0-1), 3) Key phrases that indicate the sentiment."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

## Information Extraction

### Named Entity Recognition

```python
def extract_entities(text, entity_types=None):
    """Extract named entities from text."""

    if entity_types:
        entity_prompt = f"Focus on these entity types: {', '.join(entity_types)}"
    else:
        entity_prompt = "Extract all relevant entities"

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Extract named entities from the following text. {entity_prompt}. Format as JSON with entity type and value."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example usage
entities = extract_entities(
    "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976.",
    entity_types=["PERSON", "ORGANIZATION", "LOCATION", "DATE"]
)
print("Entities:", entities)
```

### Key Information Extraction

```python
def extract_key_info(text, fields):
    """Extract specific fields from a document."""

    fields_str = ", ".join(fields)

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Extract the following information from the document: {fields_str}. Format as JSON. If a field is not found, mark it as null."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example for invoice processing
invoice_fields = ["invoice_number", "date", "total_amount", "vendor_name", "items"]
extracted_info = extract_key_info(invoice_text, invoice_fields)
```

## Document Comparison and Analysis

### Document Similarity

```python
def compare_documents(doc1, doc2):
    """Compare two documents for similarity and differences."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": "Compare these two documents. Provide: 1) Similarity score (0-1), 2) Main similarities, 3) Key differences, 4) Summary of comparison."
            },
            {
                "role": "user",
                "content": f"Document 1:\n{doc1}\n\nDocument 2:\n{doc2}"
            }
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

### Change Detection

```python
def detect_changes(original_doc, revised_doc):
    """Detect changes between document versions."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": "Identify all changes between the original and revised documents. List additions, deletions, and modifications clearly."
            },
            {
                "role": "user",
                "content": f"Original:\n{original_doc}\n\nRevised:\n{revised_doc}"
            }
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

## Batch Document Processing

### Processing Multiple Documents

```python
import asyncio
from indoxrouter import AsyncClient

async def process_documents_batch(documents, processing_function):
    """Process multiple documents concurrently."""

    client = AsyncClient(api_key="your_api_key")

    tasks = []
    for doc in documents:
        task = processing_function(client, doc)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results

async def summarize_async(client, text):
    """Async version of document summarization."""

    response = await client.chat(
        messages=[
            {
                "role": "system",
                "content": "Summarize this document in 100 words or less."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Usage
documents = ["doc1 text...", "doc2 text...", "doc3 text..."]
summaries = asyncio.run(process_documents_batch(documents, summarize_async))
```

## Document Quality Assessment

### Readability Analysis

```python
def assess_readability(text):
    """Assess document readability and provide improvement suggestions."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": "Analyze the readability of this text. Provide: 1) Reading level, 2) Clarity score (1-10), 3) Specific suggestions for improvement, 4) Complex sentences that could be simplified."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

### Content Quality Check

```python
def check_content_quality(text, criteria=None):
    """Check document quality against specific criteria."""

    if criteria:
        criteria_str = f"Focus on these criteria: {', '.join(criteria)}"
    else:
        criteria_str = "Use general quality standards"

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"Evaluate the quality of this document. {criteria_str}. Provide scores and specific feedback."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example usage
quality_criteria = ["accuracy", "completeness", "clarity", "organization"]
quality_report = check_content_quality(document, quality_criteria)
```

## Specialized Document Types

### Legal Document Processing

```python
def process_legal_document(text, task="summarize"):
    """Process legal documents with domain-specific understanding."""

    tasks = {
        "summarize": "Summarize this legal document, highlighting key legal points, obligations, and important dates.",
        "extract_clauses": "Extract and list all important clauses, terms, and conditions from this legal document.",
        "risk_analysis": "Identify potential legal risks, ambiguities, or concerning clauses in this document."
    }

    prompt = tasks.get(task, tasks["summarize"])

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"{prompt} Use legal terminology appropriately and be precise."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o"  # Use more capable model for legal analysis
    )

    return response["data"]
```

### Scientific Paper Processing

```python
def process_research_paper(text, section="abstract"):
    """Process scientific papers with academic focus."""

    sections = {
        "abstract": "Extract and summarize the abstract, highlighting research objectives, methods, and key findings.",
        "methodology": "Analyze and summarize the research methodology, including data collection and analysis methods.",
        "findings": "Extract and summarize the key findings, results, and their significance.",
        "citations": "Extract all citations and references mentioned in this paper."
    }

    prompt = sections.get(section, sections["abstract"])

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": f"{prompt} Maintain scientific accuracy and use appropriate academic language."
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o"
    )

    return response["data"]
```

## Document Generation and Enhancement

### Document Enhancement

```python
def enhance_document(text, enhancement_type="improve_clarity"):
    """Enhance document quality and readability."""

    enhancements = {
        "improve_clarity": "Rewrite this text to improve clarity and readability while maintaining all original information.",
        "professional_tone": "Rewrite this text in a more professional and formal tone.",
        "simplify": "Simplify this text for a general audience while keeping all important information.",
        "expand": "Expand this text with additional relevant details and explanations."
    }

    prompt = enhancements.get(enhancement_type, enhancements["improve_clarity"])

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {"role": "user", "content": text}
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]
```

### Template-Based Generation

```python
def generate_from_template(template, data):
    """Generate documents from templates and data."""

    response = client.chat(
        messages=[
            {
                "role": "system",
                "content": "Fill in the following template with the provided data. Maintain the template structure and format."
            },
            {
                "role": "user",
                "content": f"Template:\n{template}\n\nData:\n{data}"
            }
        ],
        model="openai/gpt-4o-mini"
    )

    return response["data"]

# Example usage
email_template = """
Subject: {subject}

Dear {recipient_name},

{opening_paragraph}

{main_content}

{closing_paragraph}

Best regards,
{sender_name}
"""

email_data = {
    "subject": "Project Update",
    "recipient_name": "John Doe",
    "opening_paragraph": "I hope this email finds you well.",
    "main_content": "I wanted to provide you with an update on our current project status...",
    "closing_paragraph": "Please let me know if you have any questions.",
    "sender_name": "Jane Smith"
}

generated_email = generate_from_template(email_template, str(email_data))
```

This comprehensive guide covers the main document processing capabilities available through IndoxRouter, enabling you to build sophisticated document analysis and processing systems.

_Last updated: Nov 08, 2025_