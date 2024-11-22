"""A command-line tool to interact with DuckDuckGo Chat API."""
from setuptools import setup, find_packages

setup(
    name="hey-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx[socks]>=0.24.1",
        "toml>=0.10.2",
        "rich>=13.7.0",
        "click>=8.1.7",
        "InquirerPy",
    ],
    entry_points={
        'console_scripts': [
            'hey=hey.__main__:cli',
        ],
    },
    author="Arslan Rejepow",
    author_email="arslanrejepow223@gmail.com",
    description="A command-line tool to interact with DuckDuckGo Chat API from your terminal",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/leen2233/hey-py",
    python_requires=">=3.8",
    keywords="cli chat ai duckduckgo",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Utilities",
    ],
)
