# Author  : Prof. MM Ghassemi <ghassem3@msu.edu>
# Access instance using `docker exec -it hw3-container_flask-app bash`

# Use Python 3.8 slim image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080
ENV FLASK_ENV=production

# Expose the port
EXPOSE 8080 

# Start the application
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app
# ----------------------------------------------------- 