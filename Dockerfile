FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY scripts/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent service and agents
COPY scripts/agent_service.py .
COPY scripts/agents/ ./agents/

# Render expects port 8080
ENV PORT=8080
EXPOSE 8080

# Run with uvicorn
CMD uvicorn agent_service:app --host 0.0.0.0 --port ${PORT}
