"""
Setup configuration for Zara Assistant.
Handles package installation, dependencies, and CLI entry point.
"""

import os
from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="zara-assistant",
    version="1.0.0",
    description="An offline-first voice assistant powered by local LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/zara-assistant",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'zara': [
            'models/*',
            'config/*',
            'data/*'
        ]
    },
    entry_points={
        'console_scripts': [
            'zara-assistant=zara.main:main',
        ],
    },
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Desktop Environment :: Desktop Assistant',
    ],
    keywords='voice assistant, offline, LLM, whisper, ollama',
)