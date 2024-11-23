from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pydbconnect",
    version="0.1.0",
    author="Peter Heller",
    author_email="pheller@qc.cuny.edu,
    description="A flexible database connection management library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pydatabaseconnection",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'isort>=5.0',
            'mypy>=0.910',
            'flake8>=3.9',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)