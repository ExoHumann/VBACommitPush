from setuptools import setup, find_packages

setup(
    name="vbacommitpush",
    version="0.1.0",
    description="VBA Commit Push tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Add other dependencies here as needed
    ],
    entry_points={
        "console_scripts": [
            "vbacommitpush=vbacommitpush.main:main",
            "spotviso=vbacommitpush.spotviso:main",
        ],
    },
)