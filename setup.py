#!/usr/env/python
from setuptools import setup, find_packages
import re
import os
import codecs

dir = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(dir, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r") as doc:
    long_description = doc.read()

setup(
    name="aws_resources",
    version=find_version("aws_resources", "__init__.py"),
    author="Manas Maiti",
    author_email="manas.maiti@gmail.com",
    description="Query AWS Resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mannyci/aws_resources",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ],
    keywords='aws boto3 python3 resources regions services',
    python_requires='>=3.2',
    install_requires=[
        'boto3>=1.12.1',
        'botocore>=1.15.1',
        'urllib3>=1.25.1'
    ],
    entry_points={
        'console_scripts': [
            'aws-resources=aws_resources.cli:main',
            'aws_resources=aws_resources.cli:main',
        ],
    },
)