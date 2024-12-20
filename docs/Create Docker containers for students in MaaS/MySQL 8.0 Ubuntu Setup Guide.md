# MySQL 8.0 Ubuntu Setup Guide

📚 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Directory Structure](#directory-structure)
  - [Dockerfile](#dockerfile)
  - [Startup Script](#startup-script)
  - [Building and Running](#building-and-running)
- [Configuration](#configuration)
- [Usage](#usage)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

🔧 Before beginning, ensure you have:

- Ubuntu 24.04 installed
- Docker installed and configured
- Minimum 2GB RAM
- Tailscale account
- Internet connectivity

## Installation

### Directory Structure

Create the necessary directory structure:

```bash
mkdir -p ~/mysql-project/{data,backup,config,scripts}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Use MySQL 8.0 on Ubuntu as base image
FROM mysql:8.0

# Labels for image metadata
LABEL maintainer="Database Administrator" \
      version="1.0" \
      description="MySQL 8.0 with Tailscale and Development Tools"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=en_US.UTF-8

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg2 \
    apt-transport-https \
    software-properties-common \
    python3-pip \
    unzip \
    git \
    vim \
    htop \
    iputils-ping \
    dnsutils \
    net-tools \
    mycli \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for database management tools
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# Install Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null && \
    curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | tee /usr/share/keyrings/tailscale-archive-keyring.list >/dev/null && \
    apt-get update && \
    apt-get install -y tailscale && \
    rm -rf /var/lib/apt/lists/*

# Install MySQL Workbench
RUN apt-get update && \
    apt-get install -y mysql-workbench && \
    rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/lib/mysql-files \
    /var/lib/mysql-backup \
    /var/lib/mysql-scripts \
    /etc/mysql/conf.d

# Copy custom MySQL configuration
COPY my.cnf /etc/mysql/conf.d/

# Copy startup script
COPY startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Expose ports
EXPOSE 3306 33060

# Set entry point
ENTRYPOINT ["/usr/local/bin/startup.sh"]
```

### MySQL Configuration (my.cnf)

Create a new file named `my.cnf`:

```ini
[mysqld]
# Basic Settings
pid-file        = /var/run/mysqld/mysqld.pid
socket          = /var/run/mysqld/mysqld.sock
datadir         = /var/lib/mysql
secure-file-priv= /var/lib/mysql-files
user            = mysql

# Network Settings
bind-address    = 0.0.0.0
mysqlx-bind-address = 0.0.0.0

# Character Set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB Settings
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_file_per_table = 1
innodb_flush_method = O_DIRECT
innodb_flush_log_at_trx_commit = 1

# Performance Settings
max_connections = 151
table_open_cache = 4000
tmp_table_size = 64M
max_heap_table_size = 64M
```

### Startup Script

Create a new file named `startup.sh`:

```bash
#!/bin/bash

# Start Tailscale
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
tailscale up

# Set MySQL root password from environment variable
if [ ! -z "$MYSQL_ROOT_PASSWORD" ]; then
    echo "Setting MySQL root password..."
    echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';" > /docker-entrypoint-initdb.d/init.sql
fi

# Start MySQL
exec mysqld

# Keep container running
tail -f /var/log/mysql/error.log
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t mysql-tailscale:latest .
```

2. Run the container:

```bash
docker run -d \
  --name mysql-tailscale \
  -e MYSQL_ROOT_PASSWORD='YourStrong!Passw0rd' \
  -e MYSQL_DATABASE='yourdatabase' \
  -v ~/mysql-project/data:/var/lib/mysql \
  -v ~/mysql-project/backup:/var/lib/mysql-backup \
  -v ~/mysql-project/config:/etc/mysql/conf.d \
  -v ~/mysql-project/scripts:/var/lib/mysql-scripts \
  -p 3306:3306 \
  -p 33060:33060 \
  mysql-tailscale:latest
```

## Configuration

### Tailscale Setup

1. Access container shell:

```bash
docker exec -it mysql-tailscale bash
```

2. Authenticate Tailscale:

```bash
tailscale up
```

3. Get Tailscale IP:

```bash
tailscale ip -4
```

### MySQL Configuration

1. Verify MySQL status:

```bash
mysqladmin -u root -p status
```

2. Secure the installation:

```bash
mysql_secure_installation
```

## Usage

### Accessing Components

- MySQL Server: Use the Tailscale IP with port 3306
- MySQL Workbench: Access via Chrome remote desktop
- Command-line: Use mycli for enhanced CLI experience

### Connecting to MySQL

Using mycli (enhanced MySQL CLI):

```bash
mycli -h <tailscale-ip> -u root -p
```

Using MySQL Workbench:

1. Open Chrome
2. Launch MySQL Workbench
3. Connect using Tailscale IP

## Maintenance

### Updating Components

1. Pull latest MySQL image:

```bash
docker pull mysql:8.0
```

2. Rebuild container:

```bash
docker build --no-cache -t mysql-tailscale:latest .
```

3. Replace running container:

```bash
docker stop mysql-tailscale
docker rm mysql-tailscale
# Run container command from Installation section
```

### Backup and Recovery

1. Create backup:

```bash
docker exec mysql-tailscale mysqldump -u root -p --all-databases \
  > /var/lib/mysql-backup/full_backup_$(date +%Y%m%d).sql
```

2. Restore backup:

```bash
docker exec -i mysql-tailscale mysql -u root -p < /var/lib/mysql-backup/backup_file.sql
```

## Troubleshooting

Common issues and solutions:

### MySQL Connection Issues

Check MySQL logs:

```bash
docker exec mysql-tailscale tail -f /var/log/mysql/error.log
```

### Tailscale Connectivity

Verify Tailscale status:

```bash
docker exec mysql-tailscale tailscale status
```

### Container Issues

Check container logs:

```bash
docker logs mysql-tailscale
```

### Volume Mount Issues

Verify volume mounts:

```bash
docker inspect mysql-tailscale | grep Mounts -A 20
```

### Performance Issues

Check InnoDB status:

```sql
SHOW ENGINE INNODB STATUS\G
```

Monitor system resources:

```bash
docker exec mysql-tailscale htop
```
