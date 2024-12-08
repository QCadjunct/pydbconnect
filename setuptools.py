from setuptools import setup, find_packages

setup(
    name="pydbconnect",
    version="0.1",
    packages=find_packages(),  # Automatically discover all packages in the directory
    package_dir={
        "": "core"
    },  # Specify that the root of the package is the 'core' directory
    install_requires=[
        # Add your dependencies here
        # For example: 'numpy', 'pandas'
    ],
    extras_require={
        "dev": [
            "pytest",
            # Add other development dependencies here
        ]
    },
    entry_points={
        "console_scripts": [
            # Define any command-line scripts here if needed
            # 'pydbconnect=core.module:main_function'
        ]
    },
)
