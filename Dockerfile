FROM python:3.11-slim

WORKDIR /app

# Copy the requirements files
COPY requirements-dev.txt .
COPY setup.py .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Ensure all provider dependencies are installed
RUN pip install --no-cache-dir openai>=1.0.0 tiktoken>=0.4.0 anthropic>=0.5.0 cohere>=4.0.0 cohere-api>=1.0.0 google-generativeai>=0.3.0 mistralai>=0.0.1

# Copy the application code
COPY indoxRouter/ indoxRouter/
COPY scripts/ scripts/
COPY examples/ examples/
COPY tests/ tests/
COPY pytest.ini .

# Make the database initialization script executable
RUN chmod +x scripts/init_db.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port your application might use
# Adjust this based on your specific application needs
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Initialize the database if DATABASE_URL is set\n\
if [ -n "$DATABASE_URL" ]; then\n\
  echo "Initializing database..."\n\
  python scripts/init_db.py\n\
fi\n\
\n\
# Start the application\n\
exec python -m indoxRouter\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Command to run the application
CMD ["/app/entrypoint.sh"] 