# Building and Installation Instructions to construct a  Wheel

## Building the Wheel

### Prerequisites
First, ensure you have the necessary build tools installed:
```bash
pip install build wheel setuptools
```

### Creating the Wheel
Run the build command:
```bash
python -m build
```

This will create two distributions in the `dist` directory:
- A source distribution (`.tar.gz`)
- A wheel distribution (`.whl`)

## Project Structure
```
pydbconnect/
├── LICENSE
├── README.md
├── MANIFEST.in
├── pyproject.toml
├── setup.py
├── requirements.txt
├── pydatabaseconnection/
│   ├── __init__.py
│   ├── core/
│   ├── utils/
│   ├── types/
│   └── config/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── performance/
└── dist/
    ├── pydatabaseconnection-0.1.0.tar.gz
    └── pydatabaseconnection-0.1.0-py3-none-any.whl
```

## MANIFEST.in Configuration
```ini
include LICENSE
include README.md
include requirements.txt
include pyproject.toml

recursive-include tests *
recursive-exclude * __pycache__
recursive-exclude * *.py[cod]
```

## Distribution Creation

### Clean Previous Builds
```bash
rm -rf build/ dist/ *.egg-info/
```

### Create Distributions
```bash
python -m build
```

### View Created Distributions
```bash
ls dist/
```

## Installation

### Installing the Wheel
```bash
pip install dist/pydatabaseconnection-0.1.0-py3-none-any.whl
```

### Development Installation
```bash
pip install -e .[dev]
```

## Notes
- The wheel distribution (`.whl`) is a built distribution format that can be directly installed with pip
- The source distribution (`.tar.gz`) contains the source code and build instructions
- The development installation (`-e`) installs the package in "editable" mode, allowing code changes to be immediately reflected without reinstallation

## Common Issues
- If you encounter permission errors, you may need to use `sudo` or run the commands in a virtual environment
- Make sure all dependencies in `requirements.txt` are available and compatible
- Check that your Python version meets the minimum requirements specified in `pyproject.toml`