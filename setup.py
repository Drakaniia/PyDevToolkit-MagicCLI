"""
setup.py - Legacy setup.py for backward compatibility
Use pyproject.toml for modern builds
"""
from setuptools import find_packages, setup

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="magic-cli",
    version="1.0.0",
    author="Eyabnyez",
    author_email="alistairybaez574@gmail.com",
    description="A powerful, secure developer toolkit with AI-powered Git operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakaniia/PyDevToolkit-MagicCLI",
    packages=find_packages(exclude=["tests*", "docs*", "scripts*", "magic_cli*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "colorama>=0.4.4",
        "pyfiglet>=0.7",
        "termcolor>=1.1.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "pyyaml>=6.0",
        ],
        "backend": [
            "fastapi>=0.100.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib>=1.7.0",
            "flask>=2.0.0",
            "flask-sqlalchemy>=3.0.0",
            "flask-migrate>=4.0.0",
            "flask-cors>=4.0.0",
            "flask-jwt-extended>=4.0.0",
            "djangorestframework>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "magic=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["assets/**/*", "config/**/*"],
    },
    zip_safe=False,
)
