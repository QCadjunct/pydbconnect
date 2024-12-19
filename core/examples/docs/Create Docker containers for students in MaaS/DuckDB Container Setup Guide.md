# DuckDB Container Setup Guide

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
- Internet connectivity
- Python 3.8 or later (for DuckDB Python API)

## Installation

### Directory Structure

Create the necessary directory structure:

```bash
mkdir -p ~/duckdb-project/{data,extensions,scripts,notebooks}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Use Python as base image for DuckDB
FROM python:3.11-slim-bullseye

# Labels for image metadata
LABEL maintainer="Data Engineer" \
      version="1.0" \
      description="DuckDB Development Environment"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    JUPYTER_ENABLE_LAB=yes

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    duckdb \
    pandas \
    numpy \
    jupyter \
    jupyterlab \
    matplotlib \
    seaborn \
    plotly \
    duckdb-engine \
    ipython-sql

# Create working directories
RUN mkdir -p /duckdb/data \
    /duckdb/extensions \
    /duckdb/scripts \
    /duckdb/notebooks

# Set working directory
WORKDIR /duckdb

# Copy startup script
COPY startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Create initialization script
RUN echo "import duckdb\n\
conn = duckdb.connect('/duckdb/data/database.db')\n\
print('DuckDB initialized successfully')" > /duckdb/scripts/init_db.py

# Expose Jupyter port
EXPOSE 8888

# Set entry point
ENTRYPOINT ["/usr/local/bin/startup.sh"]
```

### Startup Script

Create a new file named `startup.sh`:

```bash
#!/bin/bash

# Initialize DuckDB
python /duckdb/scripts/init_db.py

# Start Jupyter Lab
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

# Keep container running
tail -f /dev/null
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t duckdb-dev:latest .
```

2. Run the container:

```bash
docker run -d \
  --name duckdb-dev \
  -v ~/duckdb-project/data:/duckdb/data \
  -v ~/duckdb-project/extensions:/duckdb/extensions \
  -v ~/duckdb-project/scripts:/duckdb/scripts \
  -v ~/duckdb-project/notebooks:/duckdb/notebooks \
  -p 8888:8888 \
  duckdb-dev:latest
```

## Configuration

### DuckDB Setup

1. Access container shell:

```bash
docker exec -it duckdb-dev bash
```

2. Start Python and initialize DuckDB:

```python
import duckdb

# Connect to database
conn = duckdb.connect('/duckdb/data/database.db')

# Configure memory limit (optional)
conn.execute("SET memory_limit='4GB'")

# Enable parallel processing
conn.execute("SET threads TO 4")
```

### Extension Management

Install and load extensions:

```python
# Install extensions
conn.execute("INSTALL httpfs")
conn.execute("INSTALL json")
conn.execute("INSTALL parquet")

# Load extensions
conn.execute("LOAD httpfs")
conn.execute("LOAD json")
conn.execute("LOAD parquet")
```

## Usage

### Accessing Components

- Jupyter Lab: `http://localhost:8888`
- Python API: Via container shell or Jupyter notebooks
- SQL Interface: Via DuckDB CLI or Python API

### Basic Operations

1. Create Table:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    age INTEGER
);
```

2. Import Data:

```python
# From CSV
conn.execute("CREATE TABLE csv_data AS SELECT * FROM read_csv_auto('/duckdb/data/data.csv')")

# From Parquet
conn.execute("CREATE TABLE parquet_data AS SELECT * FROM read_parquet('/duckdb/data/data.parquet')")

# From JSON
conn.execute("CREATE TABLE json_data AS SELECT * FROM read_json_auto('/duckdb/data/data.json')")
```

3. Query Data:

```python
# Using Python API
result = conn.execute("SELECT * FROM users").fetchdf()

# Using SQL
conn.execute("SELECT * FROM users WHERE age > 25").fetchall()
```

## Maintenance

### Backup and Recovery

1. Create backup:

```python
conn.execute("EXPORT DATABASE '/duckdb/data/backup' (FORMAT PARQUET)")
```

2. Restore backup:

```python
conn.execute("IMPORT DATABASE '/duckdb/data/backup'")
```

### Performance Optimization

1. Configure memory settings:

```sql
SET memory_limit='4GB';
SET temp_directory='/duckdb/data/temp';
```

2. Enable parallel processing:

```sql
SET threads TO 4;
```

3. Create indexes:

```sql
CREATE INDEX idx_user_id ON users(id);
```

## Troubleshooting

Common issues and solutions:

### Memory Issues

Check memory usage:

```python
conn.execute("SELECT * FROM pragma_database_size").fetchall()
```

### Performance Issues

View query profile:

```python
conn.execute("EXPLAIN ANALYZE SELECT * FROM users").fetchall()
```

### Data Loading Issues

Verify file permissions:

```bash
ls -l /duckdb/data
```

### Extension Issues

Check installed extensions:

```python
conn.execute("SELECT * FROM duckdb_extensions()").fetchall()
```

### Container Issues

Check container logs:

```bash
docker logs duckdb-dev
```

### Volume Mount Issues

Verify volume mounts:

```bash
docker inspect duckdb-dev | grep Mounts -A 20
```

This guide provides a comprehensive setup for DuckDB in a containerized environment, with support for Jupyter notebooks, data analysis, and various data formats. Would you like me to expand any particular section or add more specific details about certain features?
