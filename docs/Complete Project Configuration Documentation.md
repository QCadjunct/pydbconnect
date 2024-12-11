# PyDBConnect

## 📚 Complete Project Configuration Documentation

## Table of Contents

1. [Launch Configuration](#launch-config)
2. [VS Code Settings](#vscode-settings)
3. [Project Configuration](#project-config)
4. [Environment Variables](#env-vars)
5. [Requirements](#requirements)

[⬆️ Back to Top](#table-of-contents)

## 🚀 Launch Configuration {#launch-config}

**File: launch.json**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Debug complex_multi_db_transfer.py",
            "type": "debugpy",
            "request": "launch",
            "module": "core.examples.complex_multi_db_transfer",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Debug simple_multi_db_sync.py",
            "type": "debugpy",
            "request": "launch",
            "module": "core.examples.simple_multi_db_sync",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Debug Simple example using two DatabaseConnector instances.py",
            "type": "debugpy",
            "request": "launch",
            "module": "core.examples.Simple_example_using_two_DatabaseConnector_instances",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Debug connector.py",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/core/connector.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

[⬆️ Back to Top](#table-of-contents)

## ⚙️ VS Code Settings {#vscode-settings}

**File: settings.json**

```json
{
    // Python interpreter settings
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv-dbconnect/Scripts/python.exe",
    // Python path settings
    "python.analysis.extraPaths": [
        "${workspaceFolder}/core",
        "${workspaceFolder}/optional",
        "${workspaceFolder}/templates",
        "${workspaceFolder}/utils"
    ],
    "python.envFile": "${workspaceFolder}/.env",
    // Code analysis and formatting
    "python.analysis.typeCheckingMode": "basic",
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    // Testing configuration
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests" // Ensure this directory exists if you have tests
    ],
    // Terminal environment settings
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

### 📝 Settings Documentation

- `python.defaultInterpreterPath`: Path to the Python interpreter for your project
- `python.analysis.extraPaths`: Additional paths for Python language server to resolve imports
- `python.envFile`: Path to environment variables file
- `python.analysis.typeCheckingMode`: Level of type checking ("off", "basic", "strict")
- `python.formatting.provider`: Code formatter choice ("autopep8", "black", "yapf")
- `editor.formatOnSave`: Automatic code formatting on save
- `python.linting.enabled`: Enable/disable linting
- `python.linting.pylintEnabled`: Enable/disable Pylint
- `python.testing.pytestEnabled`: Enable Pytest testing framework
- `python.testing.pytestArgs`: Arguments for Pytest
- `terminal.integrated.env.windows`: Terminal environment variables

[⬆️ Back to Top](#table-of-contents)

## 📦 Project Configuration {#project-config}

**File: pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pydbconnect"
version = "0.1.0"
description = "A Python package for database connections and operations."
readme = "README.md"
requires-python = ">=3.8"
authors = [
    { name = "Peter Heller", email = "pheller@qc.cuny.edu" },
]
dependencies = [
    "pandas>=1.3.0",
    "pyodbc>=4.0.30",
    "psycopg2-binary>=2.9.1",
    "mysql-connector-python>=8.0.26",
    "sqlalchemy>=1.4.23",
    "python-dotenv>=0.19.0",
    "keyring>=23.0.1",
    "prettytable>=2.1.0",
    "typing_extensions>=4.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "black>=21.0",
    "isort>=5.0",
    "mypy>=0.910",
    "flake8>=3.9"
]

[tool.setuptools]
packages = ["core", "optional", "templates", "utils"]
```

[⬆️ Back to Top](#table-of-contents)

## 🔐 Environment Variables {#env-vars}

**File: .env**

```plaintext
# Python Path Configuration
PYTHONPATH=./core:./optional:./templates:./utils
PYTHONIOENCODING=utf-8

# Database Configuration for username and password for each target database engine
MSSQL_USERNAME=sa
MSSQL_PASSWORD=PH@123456789
MYSQL_USERNAME=root
MYSQL_PASSWORD=Password
POSTGRESQL_USERNAME=postgres
POSTGRESQL_PASSWORD=Password
SQLITE3_USERNAME=root
SQLITE3_PASSWORD=Password
DUCKDB_USERNAME=Quackster
DUCKDB_PASSWORD=MilkAndQuackers
PSYCOPG2_USERNAME=postgres
PSYCOPG2_PASSWORD=Password

# Additional Environment Variables
DEBUG=True
LOG_LEVEL=INFO
```

[⬆️ Back to Top](#table-of-contents)

## 📋 Requirements {#requirements}

**File: requirements.txt**

```plaintext
# Empty file - dependencies are managed through pyproject.toml
```

### 📌 Note about Requirements

The project uses `pyproject.toml` for dependency management instead of `requirements.txt`. All dependencies are defined in the `[project.dependencies]` and `[project.optional-dependencies]` sections of `pyproject.toml`.

[⬆️ Back to Top](#table-of-contents)
