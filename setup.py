"""Setup script for the spot package."""

from setuptools import setup, find_packages

setup(
    name="spot",
    version="0.1.0",
    description="VBA data processing tool with logging support",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'spotviso=spot.cli:main',
        ],
    },
    python_requires='>=3.6',
    install_requires=[
        # No external dependencies for now
    ],
)