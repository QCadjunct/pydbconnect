# 🌟 Windows 11 Pro Docker Setup with Fabric and AI Tools

## 📑 Table of Contents
- [Prerequisites](#prerequisites)
- [Base System Setup](#base-system-setup)
- [Docker Container Versions](#docker-container-versions)
  - [Standalone Version](#standalone-version)
  - [Kubernetes Version](#kubernetes-version)
- [Environment Variables](#environment-variables)
- [Installation Methods](#installation-methods)
- [Volume Configuration](#volume-configuration)
- [AI Integration](#ai-integration)

## 🔧 Prerequisites
[↑ Back to Top](#table-of-contents)

- Windows 11 Pro licensed version
- NVIDIA RTX 4090 GPU
- WSL2 enabled
- Docker Desktop installed
- Visual Studio Code
- Git and GitHub account

## 🖥️ Base System Setup
[↑ Back to Top](#table-of-contents)

1. **Windows Base Image Setup**
```dockerfile
FROM dockur/windows:11-pro

# Set metadata
LABEL maintainer="Your Name <your.email@domain.com>"
LABEL description="Windows 11 Pro with Fabric, CUDA, and AI tools"

# Set environment variables
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

2. **CUDA Toolkit and WSL2 Setup**
```dockerfile
# Install CUDA Toolkit
RUN curl -O https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda_12.3.0_545.84_windows.exe && \
    start /wait cuda_12.3.0_545.84_windows.exe -s && \
    del cuda_12.3.0_545.84_windows.exe

# Enable WSL2
RUN dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart && \
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

## 🐳 Docker Container Versions
[↑ Back to Top](#table-of-contents)

### Standalone Version
```dockerfile
# Standalone version with auto-restart
version: '3.8'
services:
  fabric-standalone:
    build: .
    restart: unless-stopped
    volumes:
      - python-libs:/usr/local/lib/python3.9/site-packages
      - ollama-models:/root/.ollama
      - fabric-patterns:/root/.fabric/patterns
      - vscode-workspace:/workspace
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Kubernetes Version
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fabric-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fabric
  template:
    metadata:
      labels:
        app: fabric
    spec:
      containers:
      - name: fabric
        image: your-registry/fabric-image:tag
        volumeMounts:
        - name: python-libs
          mountPath: /usr/local/lib/python3.9/site-packages
        - name: ollama-models
          mountPath: /root/.ollama
        - name: fabric-patterns
          mountPath: /root/.fabric/patterns
        - name: vscode-workspace
          mountPath: /workspace
      volumes:
      - name: python-libs
        persistentVolumeClaim:
          claimName: python-libs-pvc
      - name: ollama-models
        persistentVolumeClaim:
          claimName: ollama-models-pvc
      - name: fabric-patterns
        persistentVolumeClaim:
          claimName: fabric-patterns-pvc
      - name: vscode-workspace
        persistentVolumeClaim:
          claimName: vscode-workspace-pvc
```

## 🌍 Environment Variables
[↑ Back to Top](#table-of-contents)

```bash
# Golang environment setup
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$GOROOT/bin:$HOME/.local/bin:$PATH

# CUDA environment variables
export CUDA_HOME=/usr/local/cuda
export PATH=$PATH:$CUDA_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Docker volumes
export PYTHON_LIBS_PATH=/usr/local/lib/python3.9/site-packages
export OLLAMA_MODELS_PATH=/root/.ollama
export FABRIC_PATTERNS_PATH=/root/.fabric/patterns
export VSCODE_WORKSPACE_PATH=/workspace
```

## 📦 Installation Methods
[↑ Back to Top](#table-of-contents)

### Latest Release Binaries

**Windows (amd64)**:
```bash
curl -L https://github.com/danielmiessler/fabric/releases/latest/download/fabric-windows-amd64.exe > fabric.exe && fabric.exe --version
```

**From Source**:
```bash
# Install Go first
go install github.com/danielmiessler/fabric@latest
```

## 💾 Volume Configuration
[↑ Back to Top](#table-of-contents)

```yaml
volumes:
  python-libs:
    driver: local
  ollama-models:
    driver: local
  fabric-patterns:
    driver: local
  vscode-workspace:
    driver: local
```

## 🤖 AI Integration
[↑ Back to Top](#table-of-contents)

### Ollama Setup
```dockerfile
# Install Ollama
RUN curl -L https://ollama.ai/download/ollama-linux-amd64 -o /usr/local/bin/ollama && \
    chmod +x /usr/local/bin/ollama

# Install OpenWebUI
RUN git clone https://github.com/open-webui/open-webui.git && \
    cd open-webui && \
    docker-compose up -d
```

### OpenWebUI Configuration
```yaml
version: '3'
services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:3000"
    environment:
      - OLLAMA_API_BASE_URL=http://ollama:11434/api
    depends_on:
      - ollama
```
