# Creating a Python Wheel for PyDBConnect

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Required Files](#required-files)
4. [Setup Configuration](#setup-configuration)
5. [Building the Wheel](#building-the-wheel)
6. [Testing the Wheel](#testing-the-wheel)
7. [Publishing to PyPI](#publishing-to-pypi)
8. [Advanced Configuration](#advanced-configuration)

## Overview

This guide explains how to create a Python wheel for PyDBConnect, making it easily distributable and installable via pip.

### What is a Python Wheel?
- 🎡 A built-package format for Python
- 📦 Contains all necessary files for installation
- 🚀 Faster installation than source distributions
- ✨ Pre-built binaries when applicable

## Project Structure

```plaintext
pydbconnect/
├── src/
│   └── pydbconnect/
│       ├── __init__.py
│       ├── connection.py
│       ├── descriptors.py
│       ├── exceptions.py
│       ├── utils.py
│       └── db_constants/
│           ├── __init__.py
│           ├── enum_connection_constants.py
│           └── database_connection_constants.py
├── tests/
│   ├── __init__.py
│   ├── test_connection.py
│   └── test_utils.py
├── docs/
│   └── index.md
├── LICENSE
├── README.md
├── pyproject.toml
├── setup.cfg
└── setup.py
```

## Required Files

### 1. pyproject.toml
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
write_to = "src/pydbconnect/_version.py"

[tool.black]
line-length = 88
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
```

### 2. setup.cfg
```ini
[metadata]
name = pydbconnect
description = Modern database connectivity library with multiple engine support
long_description = file: README.md
long_description_content_type = text/markdown
author = Your Name
author_email = your.email@example.com
license = MIT
license_files = LICENSE
platforms = any
classifiers =
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Topic :: Database
    Topic :: Software Development :: Libraries

[options]
package_dir =
    = src
packages = find:
install_requires =
    pandas>=1.3.0
    pyodbc>=4.0.30
    psycopg2-binary>=2.9.0
    prettytable>=2.0.0
    python-dotenv>=0.19.0

[options.packages.find]
where = src

[options.extras_require]
mssql =
    pyodbc>=4.0.30
postgres =
    psycopg2-binary>=2.9.0
mysql =
    mysql-connector-python>=8.0.26
dev =
    pytest>=6.0
    black
    isort
    mypy
    flake8
docs =
    mkdocs
    mkdocstrings[python]
```

### 3. setup.py
```python
from setuptools import setup

setup()
```

## Building the Wheel

### 1. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

### 2. Install Build Requirements
```bash
pip install --upgrade pip
pip install build wheel setuptools twine
```

### 3. Build the Wheel
```bash
# Build both wheel and sdist
python -m build

# Build only wheel
python -m build --wheel
```

Output structure:
```plaintext
dist/
├── pydbconnect-0.1.0-py3-none-any.whl
└── pydbconnect-0.1.0.tar.gz
```

## Testing the Wheel

### 1. Local Installation Testing
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # Unix/MacOS
# or
test_env\Scripts\activate     # Windows

# Install from wheel
pip install dist/pydbconnect-0.1.0-py3-none-any.whl
```

### 2. Verification Script
```python
# test_installation.py
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Create connection
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="test_db"
).connect_to_database()

# Test query
result = db.execute_sql_to_prettytable("SELECT version()")
print(result)
```

### 3. Run Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## Publishing to PyPI

### 1. Test PyPI First
```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ pydbconnect
```

### 2. Production PyPI
```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Advanced Configuration

### 1. Database-Specific Dependencies
```bash
# Install with MSSQL support
pip install pydbconnect[mssql]

# Install with PostgreSQL support
pip install pydbconnect[postgres]

# Install with MySQL support
pip install pydbconnect[mysql]

# Install all database supports
pip install pydbconnect[all]
```

### 2. Development Installation
```bash
# Install with development dependencies
pip install -e .[dev]
```

### 3. Version Management
```python
# src/pydbconnect/__init__.py
from ._version import version as __version__

__all__ = ['DatabaseConnection', 'TargetDatabaseEngine', '__version__']
```

### 4. Pre-release Versioning
```toml
# pyproject.toml
[tool.setuptools_scm]
write_to = "src/pydbconnect/_version.py"
version_scheme = "post-release"
local_scheme = "dirty-tag"
```

## Best Practices

1. 📝 Documentation:
   ```bash
   # Generate documentation
   pip install -e .[docs]
   mkdocs serve
   ```

2. 🧪 Quality Checks:
   ```bash
   # Run all checks
   black src/
   isort src/
   mypy src/
   flake8 src/
   ```

3. 🔄 CI/CD Integration:
   ```yaml
   # .github/workflows/build.yml
   name: Build and Test
   on: [push, pull_request]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Build and test
           run: |
             python -m pip install build
             python -m build
   ```

Would you like me to add any specific sections or provide more examples for any part?