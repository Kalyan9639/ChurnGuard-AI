# Stage 1: Use a slim, secure, and specific Python version as the base image
FROM python:3.10-slim-bullseye

# Set environment variables for Python best practices in containers
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Create a non-root user for security
# This prevents the application from running with root privileges
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy the requirements file first to leverage Docker's layer caching.
# Dependencies will only be re-installed if requirements.txt changes.
# Also, set the ownership of the file to the non-root user.
COPY --chown=appuser:appgroup requirements.txt .

# Install dependencies using pip
# --no-cache-dir reduces the image size
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copy the rest of your application code into the container
# This includes ai_model.py and the 'models' directory.
# Set ownership for all copied files.
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

# Set the port the container will listen on.
# Cloud Run will automatically inject its own PORT environment variable,
# but it's good practice to set a default and expose it.
ENV PORT 8080
EXPOSE 8080

# Define the command to run your FastAPI application using Uvicorn.
# --host 0.0.0.0 makes the server accessible from outside the container.
# The port is set to the one defined by the PORT environment variable.
CMD ["uvicorn", "ai_model:app", "--host", "0.0.0.0", "--port", "8080"]
