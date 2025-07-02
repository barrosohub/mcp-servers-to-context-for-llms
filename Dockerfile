# ---- Base Stage ----
# Use an official, slim Python image as a parent image
# Using a specific version (e.g., 3.11) is recommended for reproducibility
FROM python:3.11-slim as base

# Set environment variables to prevent writing .pyc files and to run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app


# ---- Builder Stage ----
# This stage is for installing dependencies
FROM base as builder

# Install build dependencies if any (e.g., for compiling C extensions)
# RUN apt-get update && apt-get install -y build-essential

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Create a virtual environment and install dependencies
# Using a virtual environment is a good practice even inside a container
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# This is the final, production-ready image
FROM base as final

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the path to include the virtual environment's bin directory
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user for security
# Running applications as a non-root user is a critical security best practice
RUN useradd --create-home appuser
USER appuser

# Set the working directory for the non-root user
WORKDIR /home/appuser

# Copy the application source code
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# Define the command to run the application
# Use uvicorn to run the FastAPI application
# --host 0.0.0.0 makes the application accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
