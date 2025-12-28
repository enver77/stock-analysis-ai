FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directory for model metadata if it doesn't exist
RUN touch model_metadata.json && chmod 666 model_metadata.json

# Expose port (Hugging Face Spaces uses 7860 by default)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
