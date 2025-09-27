# Stage 1: Use an official Python runtime as a parent image
# Using a slim version to keep the final image size smaller.
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container first
# This allows Docker to cache the installed packages layer if requirements.txt doesn't change
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code and the models directory into the container
COPY ai_model.py .
COPY models/ ./models/

# Expose the port the app will run on. Google Cloud Run expects port 8080 by default.
EXPOSE 8080

# Define the command to run your FastAPI application using Uvicorn
# Uvicorn will listen on 0.0.0.0 to be accessible from outside the container.
# The port is set to 8080 to match the EXPOSE instruction.
CMD ["uvicorn", "ai_model:app", "--host", "0.0.0.0", "--port", "8080"]
```
