from setuptools import setup, find_packages
import os

def read_file(filename):
    """Read the contents of a file and return as a string."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def check_required_files():
    """Ensure required files exist before setup."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = ['requirements.txt', 'readme.md'] 
    for filename in required_files:
        # Create the full path to the required file
        file_path = os.path.join(base_dir, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Required file '{filename}' not found.")

def get_requirements(filename):
    """Parse a requirements file and return a list of requirements."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(file_path) as f:
        return f.read().splitlines()

def print_setup_info(name):
    """Print package setup information."""
    print(f"Setting up {name}...")

# Ensure required files exist
check_required_files()

# Setup configuration
name = "applicare-ai"
print_setup_info(name)

# Setup configuration
setup(
    name="applicare-ai",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "applicare-ai = utils.cli.cli:cli",
        ]
    },
    author="applicare-ai",
    author_email="noreplay@applicare-ai.com",
    description="welcome to applicare-ai",
    url='https://bitbucket.org/arcturusinternal/applicare_ai',
    long_description=read_file("readme.md"),
    long_description_content_type="text/markdown",
    python_requires='>=3.6, <3.13',
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=get_requirements('requirements.txt'),
    extras_require={
        "dev": ["pytest", "wheel", "twine", "black", "setuptools"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
        "test": ["pytest-cov"],
    },
    dependency_links=[
        "git+ssh://git@github.com/infinity-sandbox/predictive-monitoring.git@14c737c247f36e3"
        "264deea5c4b9e0b0b940d17ba#egg=applicare_ai&subdirectory=server"
    ]
)