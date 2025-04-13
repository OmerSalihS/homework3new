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
    netcat-traditional \
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

# Create MySQL configuration file
RUN echo "[mysqld]\n\
bind-address = 0.0.0.0\n\
skip-networking = false\n\
skip-name-resolve\n\
default-authentication-plugin = mysql_native_password" > /etc/mysql/conf.d/mysql.cnf

# Create startup script
RUN echo '#!/bin/bash\n\
\n\
# Start MySQL\n\
service mysql start\n\
\n\
# Wait for MySQL to be ready\n\
until mysqladmin ping -h localhost --silent; do\n\
    echo "Waiting for MySQL to be ready..."\n\
    sleep 1\n\
done\n\
\n\
# Create user and database\n\
mysql -e "CREATE USER IF NOT EXISTS '\''master'\''@'\''%'\'' IDENTIFIED BY '\''master'\'';"\n\
mysql -e "CREATE DATABASE IF NOT EXISTS db;"\n\
mysql -e "GRANT ALL PRIVILEGES ON db.* TO '\''master'\''@'\''%'\'';"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
\n\
# Start the application\n\
exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app' > /app/start.sh && \
chmod +x /app/start.sh

# Set environment variables
ENV PORT=8080
ENV FLASK_ENV=production
ENV MYSQL_HOST=localhost
ENV MYSQL_USER=master
ENV MYSQL_PASSWORD=master
ENV MYSQL_DATABASE=db

# Expose the port
EXPOSE 8080

# Start the application
CMD ["/app/start.sh"]
# ----------------------------------------------------- 