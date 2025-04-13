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

# Expose the ports
EXPOSE 8080 3306

# Create startup script
RUN echo '#!/bin/bash\n\
service mysql start\n\
mysql -e "CREATE DATABASE IF NOT EXISTS your_database_name;"\n\
mysql -e "CREATE USER IF NOT EXISTS your_user@localhost IDENTIFIED BY your_password;"\n\
mysql -e "GRANT ALL PRIVILEGES ON your_database_name.* TO your_user@localhost;"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app' > /app/start.sh

RUN chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]
# ----------------------------------------------------- 