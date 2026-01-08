FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api.py .
COPY data_layer.py .
COPY analysis_layer.py .
COPY adaboost_model.joblib .
COPY scaler.joblib .
COPY model_metadata.json .

# Create cache directory for Hugging Face transformers
RUN mkdir -p /app/cache
ENV TRANSFORMERS_CACHE=/app/cache
RUN chmod -R 777 /app/cache

# Expose port 7860 (Hugging Face Default)
EXPOSE 7860

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
