# 🔍 Debugging Python Database Connector Tutorial

## 📑 Table of Contents

1. [Overview](#overview)
2. [Project Structure](#structure)
3. [Setup Instructions](#setup)
4. [Running the Demo](#running)
5. [Understanding the Output](#output)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

## 🎯 Overview {#overview}

This tutorial explains how to properly run and debug the MSSQL demo using VS Code. The successful output demonstrates database connectivity, query execution, and data retrieval.

[↑ Back to TOC](#-table-of-contents)

## 📁 Project Structure {#structure}

```
pydbconnect/
├── core/
│   ├── __init__.py
│   ├── connector.py
│   └── examples/
│       ├── __init__.py
│       └── mssql_demo.py
├── .env
├── .vscode/
│   ├── launch.json
│   └── settings.json
└── pyproject.toml
```

[↑ Back to TOC](#-table-of-contents)

## 🛠️ Setup Instructions {#setup}

### Prerequisites

- ✅ VS Code installed
- ✅ Python extension for VS Code
- ✅ Virtual environment activated
- ✅ Project dependencies installed

### Steps

1. **Activate Virtual Environment**

   ```bash
   cd Z:\VSCODE Projects\PythonProjects\pydbconnect\pydbconnect
   .venv-db_connect\Scripts\activate
   ```

2. **Verify Location**

   ```bash
   # Should be in project root
   pwd
   # Output: Z:\VSCODE Projects\PythonProjects\pydbconnect\pydbconnect
   ```

[↑ Back to TOC](#-table-of-contents)

## ▶️ Running the Demo {#running}

### Method 1: VS Code Debug

1. Open mssql_demo.py
2. Select "Debug Core Example" configuration
3. Press F5

### Method 2: Command Line

```bash
python -m core.examples.mssql_demo
```

[↑ Back to TOC](#-table-of-contents)

## 📊 Understanding the Output {#output}

### Expected Output Structure

```
Initializing connector...
Testing connection...
Executing queries...

1. SQL Server Version:
[Version Table]

2. Sample Products:
[Products Table]

Demo completed.
```

### Key Components

| Section | Purpose | Success Indicator |
|---------|---------|-------------------|
| Initialization | Setup connection | "Initializing connector..." |
| Connection Test | Verify DB access | "Testing connection..." |
| Version Check | Confirm SQL Server | Version table displays |
| Data Query | Test data retrieval | Products table shows |

[↑ Back to TOC](#-table-of-contents)

## ❗ Troubleshooting {#troubleshooting}

### Common Issues

1. **Wrong Directory**
   - 🔴 Symptom: Module not found
   - ✅ Solution: Ensure you're in project root

2. **Import Errors**
   - 🔴 Symptom: Unable to import core.connector
   - ✅ Solution: Verify PYTHONPATH in launch.json

3. **Connection Failed**
   - 🔴 Symptom: Database connection error
   - ✅ Solution: Check credentials in .env file

[↑ Back to TOC](#-table-of-contents)

## 🚀 Next Steps {#next-steps}

### Further Development

1. Add more test queries
2. Try different connection options
3. Implement error handling tests
4. Add performance monitoring

### Debug Tips

- Set breakpoints in VS Code
- Use Watch window for variables
- Check Debug Console for output

[↑ Back to TOC](#-table-of-contents)

---
> 💡 **Pro Tip**: Always run examples through their modules (`-m core.examples.mssql_demo`) rather than directly running the connector.py file.
