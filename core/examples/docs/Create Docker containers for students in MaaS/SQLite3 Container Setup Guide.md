# SQLite3 Container Setup Guide

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
- Minimum 1GB RAM
- Internet connectivity
- Basic understanding of SQLite

## Installation

### Directory Structure

Create the necessary directory structure:

```bash
mkdir -p ~/sqlite-project/{data,backup,config,scripts,tools}
```

### Dockerfile

Create a new file named `Dockerfile`:

```dockerfile
# Use Ubuntu 24.04 as base image
FROM ubuntu:24.04

# Labels for image metadata
LABEL maintainer="Database Administrator" \
      version="1.0" \
      description="SQLite3 with Development Tools"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=en_US.UTF-8 \
    SQLITE_VERSION=3.45.1

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    sqlite3 \
    sqlite3-doc \
    sqlitebrowser \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    vim \
    build-essential \
    tcl \
    tcl-dev \
    readline-common \
    libreadline-dev \
    zlib1g-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SQLite browser
RUN apt-get update && apt-get install -y \
    sqlitebrowser \
    && rm -rf /var/lib/apt/lists/*

# Install Python SQLite tools
RUN pip3 install \
    sqlite-utils \
    datasette \
    litecli \
    sqlite-web

# Create directories
RUN mkdir -p /data/sqlite \
    /data/backup \
    /data/scripts \
    /data/config

# Copy startup script
COPY scripts/startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Copy utility scripts
COPY scripts/backup.sh /usr/local/bin/
COPY scripts/restore.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/backup.sh /usr/local/bin/restore.sh

# Set working directory
WORKDIR /data/sqlite

# Expose port for SQLite Web interface
EXPOSE 8080

# Set entry point
ENTRYPOINT ["/usr/local/bin/startup.sh"]
```

### Startup Script

Create a new file named `startup.sh`:

```bash
#!/bin/bash

# Start SQLite Web interface
sqlite_web --host 0.0.0.0 --port 8080 /data/sqlite/main.db &

# Start Datasette (optional)
datasette --host 0.0.0.0 --port 8081 /data/sqlite/*.db &

# Keep container running
tail -f /dev/null
```

### Building and Running

1. Build the Docker image:

```bash
docker build -t sqlite3-dev:latest .
```

2. Run the container:

```bash
docker run -d \
  --name sqlite3-dev \
  -v ~/sqlite-project/data:/data/sqlite \
  -v ~/sqlite-project/backup:/data/backup \
  -v ~/sqlite-project/config:/data/config \
  -v ~/sqlite-project/scripts:/data/scripts \
  -p 8080:8080 \
  -p 8081:8081 \
  sqlite3-dev:latest
```

## Configuration

### SQLite Configuration

1. Create a new database:

```bash
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db
```

2. Set pragmas for optimization:

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;
PRAGMA mmap_size=30000000000;
PRAGMA cache_size=-2000000;
```

### Web Interface Setup

1. Access SQLite Web interface:
   - Open browser: `http://localhost:8080`

2. Access Datasette interface:
   - Open browser: `http://localhost:8081`

## Usage

### Command Line Tools

#### Using SQLite CLI

```bash
# Direct SQL commands
docker exec -it sqlite3-dev sqlite3 /data/sqlite/main.db

# Using litecli (enhanced CLI)
docker exec -it sqlite3-dev litecli /data/sqlite/main.db
```

#### Using sqlite-utils

```bash
# Create table
docker exec sqlite3-dev sqlite-utils create-table \
  /data/sqlite/main.db users \
  id integer name text --pk id

# Insert data
docker exec sqlite3-dev sqlite-utils insert \
  /data/sqlite/main.db users \
  '{"id": 1, "name": "John Doe"}'
```

### Python Integration

Create a file named `db_operations.py`:

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(db_path, query, params=None):
    with get_db(db_path) as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur.fetchall()
```

## Maintenance

### Backup Strategies

1. Using sqlite3 backup:

```bash
# Create backup
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db \
  ".backup '/data/backup/main_$(date +%Y%m%d).db'"

# Restore from backup
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db \
  ".restore '/data/backup/main_20240219.db'"
```

2. Using sqlite-utils:

```bash
# Backup as SQL
docker exec sqlite3-dev sqlite-utils dump \
  /data/sqlite/main.db > backup.sql

# Restore from SQL
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db < backup.sql
```

### Database Optimization

1. Run VACUUM:

```sql
VACUUM;
VACUUM ANALYZE;
```

2. Optimize indexes:

```sql
-- Analyze index usage
ANALYZE;

-- Create indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_column ON table(column);
```

## Troubleshooting

### Common Issues and Solutions

#### Database Locked

```bash
# Check for active connections
docker exec sqlite3-dev fuser /data/sqlite/main.db

# Reset WAL file
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db \
  "PRAGMA wal_checkpoint(TRUNCATE);"
```

#### Performance Issues

```sql
-- Check database stats
PRAGMA stat;

-- Check page cache stats
PRAGMA page_count;
PRAGMA page_size;

-- Optimize cache
PRAGMA cache_size = -2000000; -- Set to 2GB
```

#### Corruption Check

```bash
# Check database integrity
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db \
  "PRAGMA integrity_check;"

# Recover corrupt database
docker exec sqlite3-dev sqlite3 /data/sqlite/main.db \
  ".backup '/data/backup/recovery.db'"
```

### Best Practices

1. Use WAL mode for better concurrency
2. Regular VACUUM operations
3. Proper index management
4. Regular backups
5. Monitor file size growth
6. Use prepared statements
7. Implement proper locking strategies

[⬆️ Back to Top](#)
