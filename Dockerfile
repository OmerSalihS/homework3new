# Author  : Prof. MM Ghassemi <ghassem3@msu.edu>
# Access instance using `docker exec -it hw3-container_flask-app bash`

# Use Ubuntu 20.04 as base image
FROM ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    mysql-server \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Configure MySQL
RUN mkdir -p /var/run/mysqld && \
    chown -R mysql:mysql /var/run/mysqld && \
    chmod 777 /var/run/mysqld

# Create startup script
RUN echo '#!/bin/bash\n\
service mysql start\n\
mysql -e "CREATE USER '\''master'\''@'\''localhost'\'' IDENTIFIED BY '\''master'\'';"\n\
mysql -e "CREATE DATABASE db;"\n\
mysql -e "GRANT ALL PRIVILEGES ON db.* TO '\''master'\''@'\''localhost'\'';"\n\
exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Set environment variables
ENV PORT=8080
ENV FLASK_ENV=production

# Expose the port
EXPOSE 8080

# Start the application
CMD ["/app/start.sh"]
# ----------------------------------------------------- 