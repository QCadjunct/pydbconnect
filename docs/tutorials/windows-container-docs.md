# Windows 11 Container Solution Guide 🪟

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Version 1: Auto-restart Docker Container](#version-1)
- [Version 2: Kubernetes Deployment](#version-2)
- [RDP Client Tools](#rdp-clients)
- [Installation Guide](#installation)
- [Troubleshooting](#troubleshooting)

## Overview [🔝](#table-of-contents)

This guide provides a complete solution for running Windows 11 in a containerized environment, based on the dockur/windows project. The solution includes both Docker standalone and Kubernetes configurations.

## Prerequisites [🔝](#table-of-contents)

- Valid Windows 11 license
- Docker Desktop 4.x or newer
- Minimum 4GB RAM allocated to Docker
- At least 50GB free disk space
- Kubernetes cluster (for Version 2)

## Version 1: Auto-restart Docker Container [🔝](#table-of-contents)

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  windows11:
    image: dockurr/windows:11-pro
    container_name: windows11_client
    environment:
      - SYSTEM_LOCALE=en-US
      - SYSTEM_LANGUAGE=en-US
      - SYSTEM_KEYBOARD=0409:00000409
      - TZ=UTC
      - AUTO_SHUTDOWN=false
      - WIDTH=1920
      - HEIGHT=1080
      - DEPTH=32
      - QUALITY=80
      - SOUND=yes
    volumes:
      - windows11_data:/windows
      - ./scripts:/scripts
    ports:
      - "3389:3389"  # RDP
      - "5900:5900"  # VNC
    restart: unless-stopped
    shm_size: '2gb'
    privileged: true

volumes:
  windows11_data:
```

### Startup Script (start.sh)

```bash
#!/bin/bash

docker-compose up -d
```

### Shutdown Script (shutdown.sh)

```bash
#!/bin/bash

docker-compose down
```

## Version 2: Kubernetes Deployment [🔝](#table-of-contents)

### Kubernetes Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: windows11-client
  namespace: windows-clients
spec:
  replicas: 1
  selector:
    matchLabels:
      app: windows11-client
  template:
    metadata:
      labels:
        app: windows11-client
    spec:
      containers:
      - name: windows11
        image: dockurr/windows:11-pro
        env:
        - name: SYSTEM_LOCALE
          value: "en-US"
        - name: SYSTEM_LANGUAGE
          value: "en-US"
        - name: SYSTEM_KEYBOARD
          value: "0409:00000409"
        - name: TZ
          value: "UTC"
        - name: WIDTH
          value: "1920"
        - name: HEIGHT
          value: "1080"
        - name: DEPTH
          value: "32"
        - name: QUALITY
          value: "80"
        ports:
        - containerPort: 3389
        - containerPort: 5900
        volumeMounts:
        - name: windows11-data
          mountPath: /windows
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
      volumes:
      - name: windows11-data
        persistentVolumeClaim:
          claimName: windows11-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: windows11-service
  namespace: windows-clients
spec:
  selector:
    app: windows11-client
  ports:
  - name: rdp
    port: 3389
    targetPort: 3389
  - name: vnc
    port: 5900
    targetPort: 5900
  type: LoadBalancer
```

## RDP Client Tools [🔝](#table-of-contents)

### macOS Clients 🍎
1. Microsoft Remote Desktop
   - Download from Mac App Store
   - Features:
     - Multi-monitor support
     - Local resource sharing
     - Smart card support

2. Royal TSX
   - Professional grade remote management
   - Supports multiple protocols
   - Advanced session management

### Linux Clients 🐧
1. Remmina
   - Installation:
     ```bash
     sudo apt-get install remmina remmina-plugin-rdp
     ```
   - Features:
     - Multiple protocol support
     - Profile management
     - Quick connect

2. FreeRDP
   - Installation:
     ```bash
     sudo apt-get install freerdp2-x11
     ```
   - Command-line usage:
     ```bash
     xfreerdp /v:localhost:3389 /u:username /p:password
     ```

## Installation Guide [🔝](#table-of-contents)

### Docker Version Setup

1. Create project directory:
```bash
mkdir windows11-container
cd windows11-container
```

2. Create required files:
```bash
touch docker-compose.yml
mkdir scripts
touch scripts/start.sh scripts/shutdown.sh
chmod +x scripts/start.sh scripts/shutdown.sh
```

3. Copy the docker-compose.yml content provided above

4. Start the container:
```bash
./scripts/start.sh
```

### Kubernetes Version Setup

1. Create namespace:
```bash
kubectl create namespace windows-clients
```

2. Apply configuration:
```bash
kubectl apply -f windows11-deployment.yml
```

3. Verify deployment:
```bash
kubectl get pods -n windows-clients
```

## Troubleshooting [🔝](#table-of-contents)

### Common Issues

1. Container fails to start
   - Check system requirements
   - Verify Docker settings
   - Review logs: `docker logs windows11_client`

2. RDP Connection Issues
   - Verify port forwarding
   - Check firewall settings
   - Confirm network connectivity

3. Performance Issues
   - Adjust container resource limits
   - Monitor system resources
   - Check host system load

### Support Commands

Check container status:
```bash
docker ps -a | grep windows11
```

View container logs:
```bash
docker logs windows11_client
```

Check Kubernetes pod status:
```bash
kubectl describe pod -n windows-clients -l app=windows11-client
```
