# PostgreSQL Docker Setup Guide

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
mkdir -p ~/postgresql-project/{data,backup,config,scripts}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Use PostgreSQL 16 on Ubuntu as base image
FROM postgres:16-bookworm

# Labels for image metadata
LABEL maintainer="Database Administrator" \
      version="1.0" \
      description="PostgreSQL 16 with Tailscale and pgAdmin"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    POSTGRES_PASSWORD=YourSecurePassword \
    POSTGRES_INITDB_ARGS="--data-checksums" \
    TZ=UTC

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
    postgresql-common \
    postgresql-client-common \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for pgAdmin web access
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

# Install pgAdmin4
RUN curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg && \
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list' && \
    apt-get update && \
    apt-get install -y pgadmin4-web && \
    rm -rf /var/lib/apt/lists/*

# Install PostgreSQL extensions
RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    postgis \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/lib/postgresql/data \
    /var/lib/postgresql/backup \
    /var/lib/postgresql/scripts \
    /var/log/postgresql

# Copy configuration files
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf
COPY startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Expose ports
EXPOSE 5432 8080

# Set entry point
ENTRYPOINT ["/usr/local/bin/startup.sh"]
```

### Startup Script

Create a new file named `startup.sh`:

```bash
#!/bin/bash

# Start Tailscale
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
tailscale up

# Initialize pgAdmin
if [ ! -f "/var/lib/pgadmin/pgadmin4.db" ]; then
    pgadmin4-setup-web
fi

# Start pgAdmin
/usr/local/bin/python3 -m pgadmin4 &

# Start PostgreSQL with custom config
exec postgres -c config_file=/etc/postgresql/postgresql.conf
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t postgres-tailscale:latest .
```

2. Run the container:

```bash
docker run -d \
  --name postgres-tailscale \
  -e POSTGRES_PASSWORD=YourSecurePassword \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=YourPgAdminPassword \
  -v ~/postgresql-project/data:/var/lib/postgresql/data \
  -v ~/postgresql-project/backup:/var/lib/postgresql/backup \
  -v ~/postgresql-project/config:/etc/postgresql \
  -v ~/postgresql-project/scripts:/var/lib/postgresql/scripts \
  -p 5432:5432 \
  -p 8080:8080 \
  postgres-tailscale:latest
```

## Configuration

### Tailscale Setup

1. Access container shell:

```bash
docker exec -it postgres-tailscale bash
```

2. Authenticate Tailscale:

```bash
tailscale up
```

3. Get Tailscale IP:

```bash
tailscale ip -4
```

### PostgreSQL Configuration

1. Configure PostgreSQL to listen on Tailscale IP:

```bash
echo "listen_addresses = '*'" >> /etc/postgresql/postgresql.conf
```

2. Update pg_hba.conf for Tailscale network:

```bash
echo "host all all $(tailscale ip -4)/16 md5" >> /etc/postgresql/pg_hba.conf
```

## Usage

### Accessing Components

- PostgreSQL: Use the Tailscale IP with port 5432
- pgAdmin: Access via Chrome at <http://localhost:8080>
- Chrome: Available for database documentation access

### Connecting to PostgreSQL

Using psql:

```bash
psql -h <tailscale-ip> -U postgres -d postgres
```

Using pgAdmin:

1. Open Chrome
2. Navigate to <http://localhost:8080>
3. Log in with configured credentials
4. Add new server using Tailscale IP

## Maintenance

### Updating Components

1. Pull latest PostgreSQL image:

```bash
docker pull postgres:16-bookworm
```

2. Rebuild container:

```bash
docker build --no-cache -t postgres-tailscale:latest .
```

3. Replace running container:

```bash
docker stop postgres-tailscale
docker rm postgres-tailscale
# Run container command from Installation section
```

### Backup and Recovery

1. Create backup:

```bash
docker exec postgres-tailscale pg_dump -U postgres -F c -f /var/lib/postgresql/backup/db.backup database_name
```

2. Restore backup:

```bash
docker exec postgres-tailscale pg_restore -U postgres -d database_name /var/lib/postgresql/backup/db.backup
```

### Database Maintenance

1. Vacuum database:

```bash
docker exec postgres-tailscale vacuumdb -U postgres -d database_name -f -z
```

2. Reindex database:

```bash
docker exec postgres-tailscale reindexdb -U postgres -d database_name
```

## Troubleshooting

Common issues and solutions:

### PostgreSQL Connection Issues

Check PostgreSQL logs:

```bash
docker exec postgres-tailscale tail -f /var/log/postgresql/postgresql.log
```

### Tailscale Connectivity

Verify Tailscale status:

```bash
docker exec postgres-tailscale tailscale status
```

### Container Issues

Check container logs:

```bash
docker logs postgres-tailscale
```

### Volume Mount Issues

Verify volume mounts:

```bash
docker inspect postgres-tailscale | grep Mounts -A 20
```

### pgAdmin Issues

Check pgAdmin logs:

```bash
docker exec postgres-tailscale tail -f /var/log/pgadmin/pgadmin4.log
```

### Performance Issues

Check system resources:

```bash
docker exec postgres-tailscale psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

Monitor connections:

```bash
docker exec postgres-tailscale psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```
