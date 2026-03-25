# Step 1: Start with a Python base image
# This gives us Linux + Python 3.13 pre-installed
FROM python:3.13-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first (Docker caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of our code
COPY api_client.py .
COPY pipeline.py .

# Step 5: Tell Docker what to run when the container starts
CMD ["python", "pipeline.py"]
