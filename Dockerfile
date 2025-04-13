# Author  : Prof. MM Ghassemi <ghassem3@msu.edu>
# Access instance using `docker exec -it hw3-container_flask-app bash`

# Use Python 3.8 slim image
FROM python:3.8-slim

# Install MySQL and other required system packages
RUN apt-get update && apt-get install -y \
    default-mysql-server \
    default-mysql-client \
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
ENV MYSQL_HOST=localhost
ENV MYSQL_PORT=3306
ENV PYTHONUNBUFFERED=1

# Expose the ports
EXPOSE 8080 3306

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start MySQL service\n\
service mysql start\n\
\n\
# Wait for MySQL to be ready\n\
until mysqladmin ping -h"localhost" --silent; do\n\
    echo "Waiting for MySQL to be ready..."\n\
    sleep 1\n\
done\n\
\n\
# Initialize database\n\
mysql -e "CREATE DATABASE IF NOT EXISTS homework3;"\n\
mysql -e "CREATE USER IF NOT EXISTS homework3@localhost IDENTIFIED BY homework3;"\n\
mysql -e "GRANT ALL PRIVILEGES ON homework3.* TO homework3@localhost;"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
\n\
# Start the application with proper logging\n\
exec gunicorn --bind :$PORT \\\n\
    --workers 1 \\\n\
    --worker-class eventlet \\\n\
    --threads 8 \\\n\
    --timeout 0 \\\n\
    --log-level debug \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    app:app' > /app/start.sh

RUN chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
# ----------------------------------------------------- 