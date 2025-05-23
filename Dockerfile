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
COPY . /app

# Set working directory
WORKDIR /app

# Define default port and set PORT environment variable
ARG DEFAULT_PORT=8000
ENV PORT=${DEFAULT_PORT}

# Expose the port the application runs on
EXPOSE ${PORT}

# Set the default command to run your application
CMD ["python", "server.py"]
