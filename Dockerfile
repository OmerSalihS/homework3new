# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
# Optimized for Google Cloud Run/App Engine deployment

# Use Python 3.8 slim image
FROM python:3.8-slim

# Install MySQL and other required system packages
RUN apt-get update && apt-get install -y \
    default-mysql-server \
    default-mysql-client \
    procps \
    && rm -rf /var/lib/apt/lists/*

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
ENV PYTHONUNBUFFERED=1
ENV MYSQL_HOST=localhost
ENV MYSQL_PORT=3306
ENV MYSQL_USER=homework3
ENV MYSQL_PASSWORD=homework3
ENV MYSQL_DATABASE=homework3

# Expose the port - Google Cloud Run will override this with its own port
EXPOSE 8080

# Create startup script with improved error handling
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting MySQL service..."\n\
service mysql start\n\
\n\
# Wait for MySQL to be ready with timeout\n\
echo "Waiting for MySQL to be ready..."\n\
timeout=60\n\
counter=0\n\
until mysqladmin ping -h"localhost" --silent || [ $counter -ge $timeout ]; do\n\
    counter=$((counter+1))\n\
    echo "Waiting for MySQL... ($counter/$timeout)"\n\
    sleep 1\n\
done\n\
\n\
if [ $counter -ge $timeout ]; then\n\
    echo "Error: MySQL did not start within the timeout period."\n\
    exit 1\n\
fi\n\
\n\
echo "Initializing database..."\n\
mysql -e "CREATE DATABASE IF NOT EXISTS homework3;"\n\
mysql -e "CREATE USER IF NOT EXISTS homework3@localhost IDENTIFIED BY homework3;"\n\
mysql -e "GRANT ALL PRIVILEGES ON homework3.* TO homework3@localhost;"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
\n\
echo "Starting the application..."\n\
exec gunicorn --bind :$PORT \\\n\
    --workers 1 \\\n\
    --worker-class eventlet \\\n\
    --threads 8 \\\n\
    --timeout 0 \\\n\
    --log-level info \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    app:app' > /app/start.sh

RUN chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]