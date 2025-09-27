# Stage 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container first
# This allows Docker to cache the installed packages layer if requirements.txt doesn't change
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- FIX: Copy all necessary application files into the WORKDIR ---
# This ensures that ai_model.py and the models/ directory are in the same place.
COPY . .

# Expose the port the app will run on. Google Cloud Run expects port 8080 by default.
EXPOSE 8080

# Define the command to run your FastAPI application using Uvicorn
CMD ["uvicorn", "ai_model:app", "--host", "0.0.0.0", "--port", "8080"]

