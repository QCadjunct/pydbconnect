# Windows Container Development Environment 🖥️
[Back to Top](#windows-container-development-environment-)

## Table of Contents 📑
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Base Image Selection](#base-image-selection)
- [Docker Configuration](#docker-configuration)
  - [Standard Docker Setup](#standard-docker-setup)
  - [Kubernetes Setup](#kubernetes-setup)
- [Client Tools](#client-tools)
- [Installation Scripts](#installation-scripts)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

## Overview
This guide provides instructions for setting up a Windows 11 development environment in a container, with SQL development tools and cross-platform remote access capabilities.

[Back to Top](#windows-container-development-environment-)

## Prerequisites
- Docker Desktop 4.x or newer
- Kubernetes (for orchestrated version)
- Valid Windows 11 license
- Minimum 8GB RAM allocated to Docker
- 50GB available storage

[Back to Top](#windows-container-development-environment-)

## Base Image Selection
We'll use the `dockur/windows` base image with Windows 11 Pro, which provides:
- Official Windows 11 Pro base
- RDP support out of the box
- Optimized container size
- Automated activation support

[Back to Top](#windows-container-development-environment-)

## Docker Configuration

### Standard Docker Setup

```dockerfile
# Dockerfile
FROM dockur/windows:11-pro

# Set metadata
LABEL maintainer="Your Organization"
LABEL version="1.0"

# Environment variables
ENV ACCEPT_EULA=Y
ENV INSTALL_TOOLS=1

# Copy installation scripts
COPY scripts/install-tools.ps1 C:/setup/
COPY scripts/startup.ps1 C:/setup/

# Run installation scripts
RUN powershell.exe -ExecutionPolicy Bypass -File C:/setup/install-tools.ps1

# Expose ports
EXPOSE 3389

# Set startup script
ENTRYPOINT ["powershell.exe", "-File", "C:/setup/startup.ps1"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  windows-dev:
    build: .
    container_name: windows-dev
    ports:
      - "3389:3389"
    volumes:
      - sql-data:/sql-data
    environment:
      - ACCEPT_EULA=Y
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

volumes:
  sql-data:
```

[Back to Top](#windows-container-development-environment-)

### Kubernetes Setup

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: windows-dev
  namespace: development
spec:
  replicas: 1
  selector:
    matchLabels:
      app: windows-dev
  template:
    metadata:
      labels:
        app: windows-dev
    spec:
      containers:
      - name: windows-dev
        image: your-registry/windows-dev:latest
        ports:
        - containerPort: 3389
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        volumeMounts:
        - name: sql-data
          mountPath: /sql-data
      volumes:
      - name: sql-data
        persistentVolumeClaim:
          claimName: sql-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: windows-dev-service
spec:
  type: LoadBalancer
  ports:
  - port: 3389
    targetPort: 3389
  selector:
    app: windows-dev
```

[Back to Top](#windows-container-development-environment-)

## Client Tools 🔧
### macOS RDP Clients
1. Microsoft Remote Desktop (Recommended)
   - Available on Mac App Store
   - Full Windows experience
   - Multi-monitor support

2. Royal TSX
   - Professional-grade client
   - Advanced features
   - Paid option

### Linux RDP Clients
1. Remmina
   - Open-source
   - Built-in to many distributions
   - Full-featured

2. FreeRDP
   - Command-line and GUI options
   - Excellent performance
   - Active development

[Back to Top](#windows-container-development-environment-)

## Installation Scripts

```powershell
# install-tools.ps1
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install SQL Server Management Studio
choco install sql-server-management-studio -y

# Install Redgate SQL Toolbelt
choco install redgate-sql-toolbelt -y

# Install DBeaver Enterprise
choco install dbeaver -y --version=enterprise

# Configure automatic startup
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "DevTools" -Value "C:\setup\startup.ps1"
```

```powershell
# startup.ps1
# Start required services
Start-Service -Name "MSSQLSERVER" -ErrorAction SilentlyContinue
Start-Service -Name "SQLSERVERAGENT" -ErrorAction SilentlyContinue

# Keep container running
while ($true) {
    Start-Sleep -Seconds 60
}
```

[Back to Top](#windows-container-development-environment-)

## Usage Guide

### Standard Docker Version
```bash
# Build the image
docker compose build

# Start the container
docker compose up -d

# Stop the container
docker compose down

# Restart the container
docker compose restart
```

### Kubernetes Version
```bash
# Apply the configuration
kubectl apply -f kubernetes-deployment.yaml

# Scale deployment
kubectl scale deployment windows-dev --replicas=0  # Stop
kubectl scale deployment windows-dev --replicas=1  # Start

# Delete deployment
kubectl delete -f kubernetes-deployment.yaml
```

[Back to Top](#windows-container-development-environment-)

## Troubleshooting
Common issues and solutions:

1. Container fails to start
   - Check Docker memory allocation
   - Verify Windows license
   - Review logs: `docker logs windows-dev`

2. RDP Connection Issues
   - Verify port mapping
   - Check network connectivity
   - Ensure RDP service is running

3. Software Installation Failures
   - Check internet connectivity
   - Verify Chocolatey installation
   - Review installation logs in C:/setup/logs

[Back to Top](#windows-container-development-environment-)
