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

# Create startup script with better error handling and logging
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting MySQL service..."\n\
service mysql start\n\
\n\
# Wait for MySQL to be ready\n\
for i in {1..30}; do\n\
    if mysql -e "SELECT 1" >/dev/null 2>&1; then\n\
        echo "MySQL is ready!"\n\
        break\n\
    fi\n\
    echo "Waiting for MySQL to be ready... ($i/30)"\n\
    sleep 1\n\
done\n\
\n\
echo "Setting up MySQL user and database..."\n\
mysql -e "CREATE USER IF NOT EXISTS '\''master'\''@'\''localhost'\'' IDENTIFIED BY '\''master'\'';"\n\
mysql -e "CREATE DATABASE IF NOT EXISTS db;"\n\
mysql -e "GRANT ALL PRIVILEGES ON db.* TO '\''master'\''@'\''localhost'\'';"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 --log-level debug app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Set environment variables
ENV PORT=8080
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8080

# Start the application
CMD ["/app/start.sh"]
# ----------------------------------------------------- 