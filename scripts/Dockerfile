FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent service
COPY agent_service.py .
COPY agents/ ./agents/

# Render expects port 8080
ENV PORT=8080
EXPOSE 8080

# Run with uvicorn
CMD uvicorn agent_service:app --host 0.0.0.0 --port ${PORT}
