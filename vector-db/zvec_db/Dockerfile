# Explicitly use the arm64 version of the base image
FROM --platform=linux/arm64 python:3.10-slim

# Install system dependencies (build-essential is often needed for C++ libraries like Zvec)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Zvec and your other dependencies
RUN pip install zvec

# Copy your application code
WORKDIR /app
COPY . .

# Run your script
CMD ["python", "demo.py"]