# Fabric 2.0 with Ollama.ai Setup Guide

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

- WSL2 Ubuntu 24.04 installed
- Docker installed and configured
- NVIDIA drivers installed
- Tailscale account

## Installation

### Directory Structure

Create the necessary directory structure:

```bash
mkdir -p ~/fabric-project/{fabric,ollama,output}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Base stage with CUDA support
FROM nvidia/cuda:12.3.1-base-ubuntu24.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV OLLAMA_HOST=0.0.0.0
ENV PATH="/root/go/bin:${PATH}"

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    golang \
    chrome-browser \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA libraries
RUN apt-get update && apt-get install -y \
    cuda-cudart-12-3 \
    cuda-nvrtc-12-3 \
    libcudnn8 \
    && rm -rf /var/lib/apt/lists/*

# Install Tailscale
RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null \
    && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/jammy.tailscale-keyring.list | tee /usr/share/keyrings/tailscale-archive-keyring.list >/dev/null \
    && apt-get update && apt-get install -y tailscale

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Fabric 2.0
RUN go install github.com/danielmiessler/fabric@latest

# Create working directories
RUN mkdir -p /app/fabric \
    /app/ollama \
    /app/output

# Create volume mount points
VOLUME ["/app/fabric", "/app/ollama", "/app/output"]

# Install OpenWebUI
RUN pip3 install openwebui

# Copy startup script
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Expose necessary ports
EXPOSE 11434 8080 3000

# Set entrypoint
ENTRYPOINT ["/startup.sh"]
```

### Startup Script

Create a new file named `startup.sh`:

```bash
#!/bin/bash

# Start Tailscale
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
tailscale up

# Start Ollama
ollama serve &

# Start OpenWebUI
openwebui --host 0.0.0.0 --port 3000 &

# Keep container running
exec "$@"
```

Make the startup script executable:

```bash
chmod +x startup.sh
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t fabric-ollama:latest .
```

2. Run the container:

```bash
docker run -d \
  --name fabric-ollama \
  --gpus all \
  -v ~/fabric-project/fabric:/app/fabric \
  -v ~/fabric-project/ollama:/app/ollama \
  -v ~/fabric-project/output:/app/output \
  -p 11434:11434 \
  -p 3000:3000 \
  fabric-ollama:latest
```

## Configuration

### Tailscale Setup

1. Access container shell:

```bash
docker exec -it fabric-ollama bash
```

2. Authenticate Tailscale:

```bash
tailscale up
```

3. Note the Tailscale IP address:

```bash
tailscale ip -4
```

### Ollama Configuration

1. Configure Ollama to use Tailscale IP:

```bash
export OLLAMA_HOST=<tailscale-ip>
```

2. Verify Ollama is running:

```bash
curl http://<tailscale-ip>:11434/api/version
```

## Usage

### Accessing Components

- Fabric CLI: `docker exec -it fabric-ollama fabric`
- Ollama API: `http://<tailscale-ip>:11434`
- OpenWebUI: `http://localhost:3000`

### Running Fabric with Ollama

```bash
docker exec -it fabric-ollama fabric prompt "Your prompt here" --model llama2
```

## Maintenance

### Updating Components

1. Pull latest base image:

```bash
docker pull nvidia/cuda:12.3.1-base-ubuntu24.04
```

2. Rebuild container:

```bash
docker build --no-cache -t fabric-ollama:latest .
```

3. Replace running container:

```bash
docker stop fabric-ollama
docker rm fabric-ollama
# Run container command from Installation section
```

## Troubleshooting

Common issues and solutions:

### GPU Access Issues

Check NVIDIA GPU access:

```bash
nvidia-smi
```

### Ollama Connection Issues

Verify Ollama status:

```bash
curl http://localhost:11434/api/version
```

### Container Issues

Check container logs:

```bash
docker logs fabric-ollama
```

### Volume Mount Issues

Verify volume mounts:

```bash
docker inspect fabric-ollama | grep Mounts -A 20
```
