# 🐍 Complete Python Development Environment Setup Guide

## 📋 Table of Contents

### 🚀 Getting Started

- [System Requirements](#system-requirements)
- [Development Tools](#dev-tools)
- [Pre-Installation Checklist](#pre-install)

[Full TOC will be expanded in the next iteration]

<a name="system-requirements"></a>

## 🖥️ System Requirements [↩️](#table-of-contents)

### Minimum Hardware Requirements

- CPU: Dual-core processor or better
- RAM: 8GB minimum (16GB recommended)
- Storage: 10GB free space
- Internet: Broadband connection required

### Software Prerequisites

- Windows 10/11 (64-bit) or Linux/macOS
- Admin privileges for installation
- PowerShell 5.0+ (Windows)
- Terminal access (Linux/macOS)

### Network Requirements

- GitHub access
- PyPI access (port 443)
- PostgreSQL port access (default 5432)

<a name="dev-tools"></a>

## 🛠️ Development Tools [↩️](#table-of-contents)

### Required Software

| Tool | Version | Purpose | Download Link |
|------|---------|---------|---------------|
| Python | 3.12+ | Core Programming | [Python Downloads](https://www.python.org/downloads/) |
| Git | 2.35+ | Version Control | [Git Downloads](https://git-scm.com/downloads) |
| VSCode | Latest | IDE | [VSCode Downloads](https://code.visualstudio.com/download) |
| PostgreSQL | 14+ | Database | [PostgreSQL Downloads](https://www.postgresql.org/download/) |

### Essential VSCode Extensions

| Extension | ID | Purpose |
|-----------|------|---------|
| Python | ms-python.python | Core Python support |
| Pylance | ms-python.vscode-pylance | Language support |
| GitLens | eamodio.gitlens | Git integration |
| Python Docstring Generator | njpwerner.autodocstring | Documentation |

<a name="pre-install"></a>

## ✅ Pre-Installation Checklist [↩️](#table-of-contents)

### System Preparation

```bash
# Check if Python is installed
python --version

# Check if Git is installed
git --version

# Check if PostgreSQL is installed (if using psql)
psql --version

# Check PowerShell version (Windows)
$PSVersionTable.PSVersion

# Check available disk space (Windows)
wmic logicaldisk get size,freespace,caption
```

### Directory Structure Verification

```plaintext
Project Root Directory Structure:
└── pydbconnect/
    ├── src/
    │   └── db_templates/
    ├── docs/
    │   └── db_templates/
    ├── tests/
    ├── zzzClaudeAI/
    ├── .venv-dbconnect/
    └── .vscode/
```

### Network Verification

```bash
# Test PyPI access
ping pypi.org

# Test GitHub access
ping github.com

# Test PostgreSQL port (default 5432)
telnet localhost 5432
```

### Permission Verification

- [ ] Admin rights available
- [ ] Directory write permissions
- [ ] Python installation permissions
- [ ] VSCode extension installation rights

### Environment Variables

Required system environment variables:

```plaintext
PYTHON_HOME=<Python installation directory>
POSTGRES_HOME=<PostgreSQL installation directory>
PATH=...;%PYTHON_HOME%;%POSTGRES_HOME%\bin;...
```

# Core Setup Guide

<a name="python-install"></a>

## 🐍 Python Installation [↩️](#table-of-contents)

### Windows Installation

1. Download Python 3.12+ from [Python Downloads](https://www.python.org/downloads/)
2. Run installer with these options:

```plaintext
✓ Install for all users
✓ Add Python to PATH
✓ Install pip
✓ Install Python test suite
```

3. Verify installation:

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check Python path
where python
```

### Path Verification

```powershell
# PowerShell command to check PATH
$env:Path -split ';' | Where-Object { $_ -like '*Python*' }
```

<a name="venv-setup"></a>

## 🌐 Virtual Environment Setup [↩️](#table-of-contents)

### Create Virtual Environment

```bash
# Navigate to project directory
cd pydbconnect

# Create virtual environment
python -m venv .venv-dbconnect

# Activate virtual environment (Windows)
.venv-dbconnect\Scripts\activate

# Verify activation
where python
pip --version
```

### Project Structure Creation

```bash
# Create directory structure
mkdir src\db_templates docs\db_templates tests zzzClaudeAI
mkdir .vscode

# Create __init__.py files
type nul > src\__init__.py
type nul > src\db_templates\__init__.py
type nul > docs\__init__.py
type nul > docs\db_templates\__init__.py
type nul > tests\__init__.py
type nul > zzzClaudeAI\__init__.py
```

<a name="vscode-config"></a>

## ⚙️ VSCode Configuration [↩️](#table-of-contents)

### Settings Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv-dbconnect/Scripts/python.exe",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src",
        "${workspaceFolder}/src/db_templates",
        "${workspaceFolder}/docs",
        "${workspaceFolder}/docs/db_templates",
        "${workspaceFolder}/tests",
        "${workspaceFolder}/zzzClaudeAI"
    ],
    "python.envFile": "${workspaceFolder}/.env",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/*.pyc": true
    }
}
```

### Environment Variables

Create `.env` file:

```plaintext
# Python Path Configuration
PYTHONPATH=./src:./src/db_templates:./docs:./docs/db_templates:./tests:./zzzClaudeAI

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password

# Development Settings
DEBUG=True
LOG_LEVEL=INFO
```

<a name="project-config"></a>

## 📁 Project Configuration [↩️](#table-of-contents)

### Dependencies Setup

Create `requirements.txt`:

```plaintext
# Core dependencies
psycopg2-binary>=2.9.1
python-dotenv>=1.0.0
pydantic>=2.5.2
sqlalchemy>=2.0.23

# Testing
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-asyncio>=0.21.1

# Code quality
black>=23.11.0
isort>=5.12.0
mypy>=1.7.1
pylint>=3.0.2

# Documentation
sphinx>=7.2.6
sphinx-rtd-theme>=1.3.0
```

### Install Dependencies

```bash
# Ensure virtual environment is activated
.venv-dbconnect\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

### Project Configuration

Create `pyproject.toml`:

```toml
[project]
name = "pydbconnect"
version = "0.1.0"
description = "Python Database Connection Project"
requires-python = ">=3.12"

[tool.setuptools]
packages = [
    "src",
    "src.db_templates",
    "docs",
    "docs.db_templates",
    "tests",
    "zzzClaudeAI"
]

[tool.pytest.ini_options]
pythonpath = [
    "src",
    "src/db_templates",
    "docs",
    "docs/db_templates",
    "tests",
    "zzzClaudeAI"
]
testpaths = ["tests"]

[tool.black]
line-length = 88
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

# Database and Testing Setup

<a name="db-setup"></a>

## 🗄️ Database Setup [↩️](#table-of-contents)

### PostgreSQL Configuration

```bash
# Create database connection file
mkdir src\db_templates\connections

# Create database configuration file
type nul > src\db_templates\connections\db_config.py
```

Create `src/db_templates/connections/db_config.py`:

```python
"""Database configuration and connection management."""
from typing import Dict, Any
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DBConfig:
    """Database configuration parameters."""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', 5432))
    database: str = os.getenv('DB_NAME', 'postgres')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', '')

    def as_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }
```

### Database Connection Manager

Create `src/db_templates/connections/db_manager.py`:

```python
"""Database connection manager."""
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from .db_config import DBConfig

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, config: DBConfig = None):
        """Initialize with configuration."""
        self.config = config or DBConfig()

    @contextmanager
    def get_connection(self):
        """Create a database connection context."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config.as_dict())
            yield conn
        finally:
            if conn is not None:
                conn.close()

    def execute_query(self, query: str, params: dict = None) -> list:
        """Execute a query and return results."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or {})
                if cur.description:
                    return cur.fetchall()
                conn.commit()
                return []
```

<a name="test-setup"></a>

## 🧪 Testing Setup [↩️](#table-of-contents)

### Test Configuration

Create `tests/conftest.py`:

```python
"""PyTest configuration and fixtures."""
import pytest
from src.db_templates.connections.db_config import DBConfig
from src.db_templates.connections.db_manager import DatabaseManager

@pytest.fixture
def db_config():
    """Provide test database configuration."""
    return DBConfig(
        host='localhost',
        port=5432,
        database='test_db',
        user='test_user',
        password='test_password'
    )

@pytest.fixture
def db_manager(db_config):
    """Provide database manager instance."""
    return DatabaseManager(db_config)
```

### Database Tests

Create `tests/test_db_connection.py`:

```python
"""Test database connections and operations."""
import pytest
from src.db_templates.connections.db_manager import DatabaseManager

def test_db_connection(db_manager):
    """Test database connection."""
    try:
        result = db_manager.execute_query("SELECT version();")
        assert result is not None
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")

def test_query_execution(db_manager):
    """Test query execution."""
    # Create test table
    create_table = """
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
    """
    db_manager.execute_query(create_table)

    # Insert test data
    insert_data = """
    INSERT INTO test_table (name) VALUES (%(name)s)
    RETURNING id, name;
    """
    result = db_manager.execute_query(insert_data, {'name': 'test'})
    assert result[0]['name'] == 'test'

@pytest.fixture(autouse=True)
def cleanup(db_manager):
    """Cleanup test database after each test."""
    yield
    db_manager.execute_query("DROP TABLE IF EXISTS test_table;")
```

<a name="ci-setup"></a>

## 🔄 Continuous Integration Setup [↩️](#table-of-contents)

### GitHub Actions

Create `.github/workflows/python-tests.yml`:

```yaml
name: Python Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: test_db
        DB_USER: test_user
        DB_PASSWORD: test_password
      run: |
        pytest tests/ -v --cov=src
```

<a name="verification"></a>

## ✅ Setup Verification [↩️](#table-of-contents)

Create `src/verify_setup.py`:

```python
"""Verify project setup and configuration."""
import os
import sys
import importlib
from pathlib import Path

def check_environment():
    """Verify environment setup."""
    checks = {
        "Python Version": sys.version,
        "Virtual Environment": sys.prefix != sys.base_prefix,
        "Project Root": Path(__file__).parent.parent.absolute(),
        "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set")
    }
    
    print("\n=== Environment Checks ===")
    for name, value in checks.items():
        print(f"{name}: {value}")

def check_imports():
    """Verify required packages."""
    required_packages = [
        "psycopg2",
        "dotenv",
        "pytest",
        "black",
        "pylint"
    ]
    
    print("\n=== Package Checks ===")
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} successfully imported")
        except ImportError as e:
            print(f"✗ {package} import failed: {str(e)}")

def main():
    """Run all verification checks."""
    print("Running setup verification...")
    check_environment()
    check_imports()

if __name__ == "__main__":
    main()
```

# Development Workflow and Documentation

<a name="workflow"></a>

## 🔄 Development Workflow [↩️](#table-of-contents)

### Git Workflow Setup

```bash
# Initialize Git repository (if not already done)
git init

# Create .gitignore
type nul > .gitignore
```

Create `.gitignore`:

```plaintext
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv-dbconnect/
venv/
ENV/

# VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# Environment Variables
.env
.env.*

# Database
*.sqlite3
*.db

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Documentation
docs/_build/
docs/api/

# IDE
.idea/
*.swp
*.swo
.DS_Store
```

### Development Standards File

Create `CONTRIBUTING.md`:

```markdown
# Contributing Guidelines

## Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints for all function arguments and return values
- Include docstrings for all modules, classes, and functions

## Git Workflow
1. Create feature branch from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes following these commit conventions:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - style: Formatting, missing semi colons, etc
   - refactor: Code restructuring
   - test: Adding tests
   - chore: Maintenance tasks

3. Push changes and create pull request:

   ```bash
   git push origin feature/your-feature-name
   ```

## Testing Requirements

- Write tests for all new features
- Maintain minimum 80% code coverage
- Run full test suite before committing:

  ```bash
  pytest tests/ -v --cov=src
  ```

## Documentation Standards

- Update documentation for all new features
- Include examples in docstrings
- Keep README.md up to date

```

<a name="docs-setup"></a>
## 📚 Documentation Setup [↩️](#table-of-contents)

### Sphinx Documentation
```bash
# Create Sphinx documentation structure
cd docs
sphinx-quickstart
```

Create `docs/conf.py`:

```python
"""Sphinx configuration file."""
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'pydbconnect'
copyright = '2024, Your Name'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True
```

### Create Documentation Structure

```plaintext
docs/
├── _static/
├── _templates/
├── api/
│   ├── db_templates.rst
│   ├── tests.rst
│   └── zzzClaudeAI.rst
├── guides/
│   ├── installation.rst
│   ├── database.rst
│   └── testing.rst
├── conf.py
└── index.rst
```

Create `docs/index.rst`:

```rst
Welcome to pydbconnect's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guides/installation
   guides/database
   guides/testing
   api/db_templates
   api/tests
   api/zzzClaudeAI

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

<a name="troubleshooting"></a>

## 🔍 Troubleshooting Guide [↩️](#table-of-contents)

### Common Issues and Solutions

Create `docs/TROUBLESHOOTING.md`:

```markdown
# Troubleshooting Guide

## Virtual Environment Issues

### Problem: Cannot Create Virtual Environment
```bash
# Error: Python not found
Solution: Verify Python installation
where python
```

### Problem: Import Errors

```bash
# Error: Module not found
Solution: Check PYTHONPATH
echo %PYTHONPATH%
```

## Database Connection Issues

### Problem: Cannot Connect to Database

1. Verify PostgreSQL is running:

```bash
# Windows
net start postgresql
# Linux
systemctl status postgresql
```

2. Check connection parameters:

```python
# Test connection
import psycopg2
conn = psycopg2.connect(
    dbname="your_database",
    user="your_username",
    password="your_password",
    host="localhost"
)
```

## VSCode Issues

### Problem: Python Interpreter Not Found

1. Command Palette (Ctrl+Shift+P)
2. "Python: Select Interpreter"
3. Choose `.venv-dbconnect` interpreter

### Problem: Linting/Formatting Not Working

1. Verify extensions installed
2. Check settings.json configuration
3. Restart VSCode

```

# Database Templates and Deployment

<a name="db-templates"></a>
## 📊 Database Templates [↩️](#table-of-contents)

### Base Repository Pattern
Create `src/db_templates/base_repository.py`:
```python
"""Base repository pattern implementation."""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for database operations."""

    def __init__(self, db_manager):
        """Initialize repository with database manager."""
        self.db = db_manager

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve a record by ID."""
        pass

    @abstractmethod
    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """Update an existing record."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a record."""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """Retrieve all records."""
        pass

class AuditMixin:
    """Mixin to add audit fields to repositories."""

    def add_audit_fields(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Add audit fields to data dictionary."""
        now = datetime.utcnow()
        if not is_update:
            data['created_at'] = now
            data['created_by'] = self.get_current_user()
        data['updated_at'] = now
        data['updated_by'] = self.get_current_user()
        return data

    def get_current_user(self) -> str:
        """Get current user for audit purposes."""
        # Implement your user context logic here
        return "system"
```

### Example Implementation

Create `src/db_templates/user_repository.py`:

```python
"""User repository implementation."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .base_repository import BaseRepository, AuditMixin

@dataclass
class User:
    """User entity."""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    is_active: bool = True
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

class UserRepository(BaseRepository[User], AuditMixin):
    """Repository for user operations."""

    def __init__(self, db_manager):
        """Initialize repository."""
        super().__init__(db_manager)
        self.table_name = "users"

    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user."""
        data = self.add_audit_fields(data)
        query = f"""
        INSERT INTO {self.table_name} (
            username, email, is_active, 
            created_at, created_by, updated_at, updated_by
        ) VALUES (
            %(username)s, %(email)s, %(is_active)s,
            %(created_at)s, %(created_by)s, %(updated_at)s, %(updated_by)s
        ) RETURNING *;
        """
        result = self.db.execute_query(query, data)
        return User(**result[0]) if result else None

    def get_by_id(self, id: int) -> Optional[User]:
        """Get user by ID."""
        query = f"""
        SELECT * FROM {self.table_name} WHERE id = %(id)s;
        """
        result = self.db.execute_query(query, {'id': id})
        return User(**result[0]) if result else None

    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """Update user."""
        data = self.add_audit_fields(data, is_update=True)
        set_clause = ", ".join([f"{k} = %({k})s" for k in data.keys()])
        query = f"""
        UPDATE {self.table_name}
        SET {set_clause}
        WHERE id = %(id)s;
        """
        data['id'] = id
        self.db.execute_query(query, data)
        return True

    def delete(self, id: int) -> bool:
        """Delete user."""
        query = f"""
        DELETE FROM {self.table_name} WHERE id = %(id)s;
        """
        self.db.execute_query(query, {'id': id})
        return True

    def list_all(self) -> List[User]:
        """List all users."""
        query = f"SELECT * FROM {self.table_name};"
        results = self.db.execute_query(query)
        return [User(**result) for result in results]
```

<a name="security"></a>

## 🔒 Security Best Practices [↩️](#table-of-contents)

### Security Configuration

Create `src/security/security_config.py`:

```python
"""Security configuration and utilities."""
import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

class SecurityUtils:
    """Security utility functions."""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt."""
        if not salt:
            salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hash_obj.hex(), salt

    @staticmethod
    def verify_password(password: str, hash_value: str, salt: str) -> bool:
        """Verify password against hash."""
        new_hash, _ = SecurityUtils.hash_password(password, salt)
        return secrets.compare_digest(new_hash, hash_value)

    @staticmethod
    def generate_token() -> str:
        """Generate secure token."""
        return secrets.token_urlsafe(32)

class AuditLogger:
    """Security audit logging."""

    @staticmethod
    def log_security_event(event_type: str, user_id: str, details: str):
        """Log security-related events."""
        timestamp = datetime.utcnow()
        # Implement your logging logic here
        print(f"{timestamp} - {event_type} - User: {user_id} - {details}")
```

<a name="deployment"></a>

## 🚀 Deployment Guidelines [↩️](#table-of-contents)

### Production Configuration

Create `config/production.py`:

```python
"""Production configuration settings."""
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProductionConfig:
    """Production environment configuration."""
    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    SECRET_KEY: str = os.getenv('SECRET_KEY', '')
    ALLOWED_HOSTS: list = os.getenv('ALLOWED_HOSTS', '*').split(',')
    
    # Security settings
    SSL_REDIRECT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    CSRF_COOKIE_SECURE: bool = True
    SECURE_HSTS_SECONDS: int = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
    
    # Logging configuration
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: getattr(self, key)
            for key in self.__annotations__
        }
```

### Deployment Script

Create `scripts/deploy.py`:

```python
"""Deployment automation script."""
import os
import subprocess
from pathlib import Path
from datetime import datetime

class Deployer:
    """Handles deployment process."""

    def __init__(self):
        """Initialize deployer."""
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path('backups') / self.timestamp

    def backup_database(self):
        """Create database backup."""
        os.makedirs(self.backup_dir, exist_ok=True)
        subprocess.run([
            'pg_dump',
            '-U', os.getenv('DB_USER'),
            '-F', 'c',
            '-b',
            '-v',
            '-f', str(self.backup_dir / 'backup.dump'),
            os.getenv('DB_NAME')
        ])

    def run_migrations(self):
        """Run database migrations."""
        subprocess.run([
            'alembic',
            'upgrade',
            'head'
        ])

    def collect_static(self):
        """Collect static files."""
        static_dir = Path('static')
        os.makedirs(static_dir, exist_ok=True)
        # Implement static file collection logic

    def deploy(self):
        """Run deployment process."""
        try:
            print("Starting deployment...")
            self.backup_database()
            self.run_migrations()
            self.collect_static()
            print("Deployment successful!")
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            # Implement rollback logic
```

## 🚀 Deployment Guidelines [↩️](#table-of-contents)

# 🚀 Quick Reference Guide

## 📋 Common Commands

### Virtual Environment

```bash
# Create virtual environment
python -m venv .venv-dbconnect

# Activate (Windows)
.venv-dbconnect\Scripts\activate

# Activate (Linux/Mac)
source .venv-dbconnect/bin/activate

# Deactivate
deactivate
```

### Package Management

```bash
# Install packages
pip install -r requirements.txt

# Update packages
pip install --upgrade -r requirements.txt

# Show installed packages
pip list

# Save requirements
pip freeze > requirements.txt
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_db_connection.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Lint code
pylint src/
```

## 🔍 Quick Checks

### Environment Verification

```python
# Check Python version
python --version

# Check virtual environment
where python  # Windows
which python  # Linux/Mac

# Check PYTHONPATH
echo %PYTHONPATH%  # Windows
echo $PYTHONPATH  # Linux/Mac
```

### Database Connection

```python
# Test database connection
python -c "
from src.db_templates.connections.db_manager import DatabaseManager
db = DatabaseManager()
result = db.execute_query('SELECT version();')
print(result)
"
```

## 📁 Project Structure

```plaintext
pydbconnect/
├── src/
│   ├── db_templates/
│   │   ├── connections/
│   │   │   ├── db_config.py
│   │   │   └── db_manager.py
│   │   └── base_repository.py
│   └── verify_setup.py
├── tests/
│   ├── conftest.py
│   └── test_db_connection.py
├── docs/
│   └── conf.py
├── zzzClaudeAI/
│   └── db_helper.py
└── requirements.txt
```

## ⚙️ Configuration Files

### VSCode Settings (`settings.json`)

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv-dbconnect/Scripts/python.exe",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src",
        "${workspaceFolder}/src/db_templates",
        "${workspaceFolder}/tests",
        "${workspaceFolder}/zzzClaudeAI"
    ]
}
```

### Environment Variables (`.env`)

```plaintext
PYTHONPATH=./src:./src/db_templates:./tests:./zzzClaudeAI
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

## 🐛 Common Issues & Solutions

### Import Issues

```plaintext
Problem: ModuleNotFoundError
Solution: Check PYTHONPATH and virtual environment activation
```

### Database Connection

```plaintext
Problem: Could not connect to PostgreSQL
Solution: 
1. Check PostgreSQL service is running
2. Verify credentials in .env
3. Check port availability
```

### VSCode Python

```plaintext
Problem: No Python interpreter selected
Solution: Ctrl+Shift+P → Python: Select Interpreter
```

## 🔄 Development Workflow

### Git Commands

```bash
# New feature branch
git checkout -b feature/name

# Stage changes
git add .

# Commit
git commit -m "feat: description"

# Push
git push origin feature/name
```

### Database Operations

```python
# Basic CRUD operations
from src.db_templates.connections.db_manager import DatabaseManager

db = DatabaseManager()

# Create
db.execute_query(
    "INSERT INTO table (column) VALUES (%(value)s)",
    {"value": "data"}
)

# Read
db.execute_query("SELECT * FROM table")

# Update
db.execute_query(
    "UPDATE table SET column = %(value)s WHERE id = %(id)s",
    {"value": "new_data", "id": 1}
)

# Delete
db.execute_query(
    "DELETE FROM table WHERE id = %(id)s",
    {"id": 1}
)
```

## 📚 Key Resources

### Documentation

- Python Docs: <https://docs.python.org/3.12/>
- PostgreSQL Docs: <https://www.postgresql.org/docs/>
- VSCode Python: <https://code.visualstudio.com/docs/python/python-tutorial>

### Testing

- pytest Docs: <https://docs.pytest.org/>
- Coverage: <https://coverage.readthedocs.io/>

### Code Quality

- Black: <https://black.readthedocs.io/>
- Pylint: <https://pylint.readthedocs.io/>
- MyPy: <https://mypy.readthedocs.io/>

## 🔐 Security Checklist

- [ ] Environment variables secured
- [ ] Database credentials protected
- [ ] SSL/TLS configured
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] Password hashing used
- [ ] Audit logging enabled

## 🚀 Deployment Guidelines [↩️](#table-of-contents)

# 🚀 Deployment Checklist

## 📋 Pre-Deployment Verification

### Code Quality

- [ ] All tests passing

  ```bash
  pytest tests/ -v --cov=src --cov-report=term-missing
  ```

- [ ] Code formatting verified

  ```bash
  black --check src/
  isort --check-only src/
  ```

- [ ] Type checking passed

  ```bash
  mypy src/
  ```

- [ ] Lint checks passed

  ```bash
  pylint src/
  ```

### Dependencies

- [ ] Requirements file updated

  ```bash
  pip freeze > requirements.txt
  ```

- [ ] Dependencies scanned for security

  ```bash
  safety check -r requirements.txt
  ```

- [ ] Virtual environment clean

  ```bash
  deactivate
  rm -rf .venv-dbconnect
  python -m venv .venv-dbconnect
  ```

### Configuration

- [ ] Environment variables documented

  ```plaintext
  Required Variables:
  - DB_HOST
  - DB_PORT
  - DB_NAME
  - DB_USER
  - DB_PASSWORD
  - SECRET_KEY
  - DEBUG
  - ALLOWED_HOSTS
  ```

- [ ] Sensitive data removed from code
- [ ] Configuration files reviewed
- [ ] Debug mode disabled

## 🔒 Security Checklist

### Database

- [ ] Connection strings secured
- [ ] Passwords hashed
- [ ] Connection pooling configured
- [ ] Backups verified
- [ ] Migrations tested

### Authentication

- [ ] SSL/TLS certificates installed
- [ ] API keys rotated
- [ ] Session handling secured
- [ ] Password policies enforced
- [ ] Rate limiting configured

### Authorization

- [ ] Permissions reviewed
- [ ] Role-based access configured
- [ ] API endpoints secured
- [ ] File permissions set
- [ ] Security headers configured

## 📦 Database Deployment

### Backup

```bash
# Backup existing database
pg_dump -U username -d dbname -F c -b -v -f backup.dump

# Verify backup
pg_restore -l backup.dump
```

### Migration

- [ ] Database migrations prepared

  ```bash
  alembic revision --autogenerate -m "deployment_changes"
  ```

- [ ] Migration scripts tested

  ```bash
  alembic upgrade head
  ```

- [ ] Rollback scripts prepared

  ```bash
  alembic downgrade -1
  ```

### Verification

- [ ] Data integrity checked
- [ ] Indexes optimized
- [ ] Query performance verified
- [ ] Connections tested

## 🔄 Production Environment

### System Requirements

- [ ] CPU allocation verified
- [ ] Memory limits set
- [ ] Disk space checked
- [ ] Network configuration verified

### Services

- [ ] PostgreSQL service running
- [ ] Backup service configured
- [ ] Monitoring service active
- [ ] Logging service enabled

### Performance

- [ ] Load balancing configured
- [ ] Caching implemented
- [ ] Static files optimized
- [ ] Database queries optimized

## 📊 Monitoring Setup

### Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'production.log',
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
}
```

### Alerts

- [ ] Error notification system
- [ ] Performance alerts
- [ ] Security alerts
- [ ] Uptime monitoring
- [ ] Resource usage alerts

## 🔄 Deployment Process

### Pre-Deploy

```bash
# Create deployment directory
mkdir -p /deploy/pydbconnect

# Copy files
cp -r src/ requirements.txt /deploy/pydbconnect/

# Set permissions
chmod -R 755 /deploy/pydbconnect
```

### Deploy

```bash
# Stop services
systemctl stop pydbconnect

# Backup
./scripts/backup.sh

# Update code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start services
systemctl start pydbconnect
```

### Post-Deploy

```bash
# Verify deployment
./scripts/verify_deployment.sh

# Monitor logs
tail -f /var/log/pydbconnect.log
```

## ✅ Post-Deployment Verification

### Testing

- [ ] Smoke tests passed
- [ ] Integration tests passed
- [ ] Performance tests passed
- [ ] Security tests passed

### Monitoring

- [ ] Logs verified
- [ ] Metrics collecting
- [ ] Alerts functioning
- [ ] Backup system verified

### Documentation

- [ ] Deployment documented
- [ ] Changes logged
- [ ] API docs updated
- [ ] README updated

## 🔄 Rollback Plan

### Triggers

- [ ] Critical bugs
- [ ] Data corruption
- [ ] Performance issues
- [ ] Security breaches

### Process

```bash
# Rollback code
git reset --hard previous_commit

# Rollback database
alembic downgrade previous_revision

# Restore backup
pg_restore -d dbname backup.dump

# Restart services
systemctl restart pydbconnect
```

## 📝 Final Checklist

- [ ] All tests passing in production
- [ ] Monitoring systems active
- [ ] Backup systems verified
- [ ] Documentation updated
- [ ] Support team notified
- [ ] Users notified of changes
- [ ] Performance baseline established
- [ ] Security scan completed

## 🚀 Deployment Checklist [↩️](#table-of-contents)
