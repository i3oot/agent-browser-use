# Use an official Python image as the base
FROM python:3.11-slim

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Playwright dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl && \
    pip install playwright && \
    playwright install-deps && \
    playwright install && \
    rm -rf /var/lib/apt/lists/*  # Clean up APT cache to reduce image size

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application files
# This will include the browser_agent directory and .env file
COPY . /app

# Set working directory
WORKDIR /app

# Add /app to PYTHONPATH to ensure agent module is found
ENV PYTHONPATH=/app

# Expose the port the ADK server will run on
EXPOSE 8080

# Set the default command to run the ADK API server
CMD ["adk", "api_server", "browser_agent.agent", "--host", "0.0.0.0", "--port", "8080"]
