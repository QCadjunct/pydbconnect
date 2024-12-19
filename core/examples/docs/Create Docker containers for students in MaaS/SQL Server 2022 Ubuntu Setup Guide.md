# SQL Server 2022 Ubuntu Setup Guide

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
- Minimum 4GB RAM
- Tailscale account
- Internet connectivity

## Installation

### Directory Structure

Create the necessary directory structure:

```bash
mkdir -p ~/sqlserver-project/{data,backup,config,scripts}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Use SQL Server 2022 on Ubuntu as base image
FROM mcr.microsoft.com/mssql/server:2022-latest-ubuntu

# Labels for image metadata
LABEL maintainer="Database Administrator" \
      version="1.0" \
      description="SQL Server 2022 with Tailscale and Chrome"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    ACCEPT_EULA=Y \
    MSSQL_PID=Developer \
    MSSQL_AGENT_ENABLED=true \
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
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
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

# Install Azure Data Studio
RUN curl -L "https://go.microsoft.com/fwlink/?linkid=2204570" -o azuredatastudio.deb && \
    apt-get update && \
    apt-get install -y ./azuredatastudio.deb && \
    rm azuredatastudio.deb && \
    rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/opt/mssql/data \
    /var/opt/mssql/log \
    /var/opt/mssql/backup \
    /var/opt/mssql/scripts

# Copy startup script
COPY startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Expose ports
EXPOSE 1433 8080

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

# Start SQL Server
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to start
sleep 10

# Start Azure Data Studio (if needed)
# /usr/bin/azuredatastudio --no-sandbox &

# Keep container running
tail -f /var/opt/mssql/log/errorlog
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t sqlserver-tailscale:latest .
```

2. Run the container:

```bash
docker run -d \
  --name sqlserver-tailscale \
  -e 'ACCEPT_EULA=Y' \
  -e 'SA_PASSWORD=YourStrong!Passw0rd' \
  -v ~/sqlserver-project/data:/var/opt/mssql/data \
  -v ~/sqlserver-project/backup:/var/opt/mssql/backup \
  -v ~/sqlserver-project/config:/var/opt/mssql/config \
  -v ~/sqlserver-project/scripts:/var/opt/mssql/scripts \
  -p 1433:1433 \
  -p 8080:8080 \
  sqlserver-tailscale:latest
```

## Configuration

### Tailscale Setup

1. Access container shell:

```bash
docker exec -it sqlserver-tailscale bash
```

2. Authenticate Tailscale:

```bash
tailscale up
```

3. Get Tailscale IP:

```bash
tailscale ip -4
```

### SQL Server Configuration

1. Set SQL Server to listen on Tailscale IP:

```bash
echo "network.ipAddressPreference=IPv4" >> /var/opt/mssql/mssql.conf
```

2. Verify SQL Server status:

```bash
systemctl status mssql-server
```

## Usage

### Accessing Components

- SQL Server: Use the Tailscale IP with port 1433
- Azure Data Studio: Access via Chrome remote desktop
- Chrome: Available for database documentation access

### Connecting to SQL Server

Using sqlcmd:

```bash
sqlcmd -S <tailscale-ip> -U sa -P '<your-password>'
```

Using Azure Data Studio:

1. Open Chrome
2. Navigate to Azure Data Studio
3. Connect using Tailscale IP

## Maintenance

### Updating Components

1. Pull latest SQL Server image:

```bash
docker pull mcr.microsoft.com/mssql/server:2022-latest-ubuntu
```

2. Rebuild container:

```bash
docker build --no-cache -t sqlserver-tailscale:latest .
```

3. Replace running container:

```bash
docker stop sqlserver-tailscale
docker rm sqlserver-tailscale
# Run container command from Installation section
```

### Backup and Recovery

1. Create backup:

```bash
docker exec sqlserver-tailscale /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P '<your-password>' \
  -Q "BACKUP DATABASE YourDB TO DISK = '/var/opt/mssql/backup/YourDB.bak'"
```

2. Restore backup:

```bash
docker exec sqlserver-tailscale /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P '<your-password>' \
  -Q "RESTORE DATABASE YourDB FROM DISK = '/var/opt/mssql/backup/YourDB.bak'"
```

## Troubleshooting

Common issues and solutions:

### SQL Server Connection Issues

Check SQL Server logs:

```bash
docker exec sqlserver-tailscale cat /var/opt/mssql/log/errorlog
```

### Tailscale Connectivity

Verify Tailscale status:

```bash
docker exec sqlserver-tailscale tailscale status
```

### Container Issues

Check container logs:

```bash
docker logs sqlserver-tailscale
```

### Volume Mount Issues

Verify volume mounts:

```bash
docker inspect sqlserver-tailscale | grep Mounts -A 20
```

### Chrome Issues

Check Chrome installation:

```bash
docker exec sqlserver-tailscale google-chrome --version
```
