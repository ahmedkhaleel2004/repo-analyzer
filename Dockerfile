FROM python:3.12-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml .

# Copy source code
COPY src/ src/

# Install dependencies
RUN pip install --no-cache-dir .

# Create results directory
RUN mkdir -p results

# Expose port for FastAPI
EXPOSE 8000

# Default to running the API server
CMD ["uvicorn", "repo_analyzer.api:app", "--host", "0.0.0.0", "--port", "8000"]
