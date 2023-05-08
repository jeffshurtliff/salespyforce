#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Synopsis:          This script is the primary configuration file for the salespyforce project
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     08 May 2023
"""

import setuptools
import codecs
import os.path


def read(rel_path):
    """This function reads the ``version.py`` script in order to retrieve the version."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    """This function retrieves the current version of the package without needing to import the
       :py:mod:`salespyforce.utils.version` module in order to avoid dependency issues."""
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delimiter = '"' if '"' in line else "'"
            return line.split(delimiter)[1]
    raise RuntimeError("Unable to find the version string")


with open('README.md', 'r') as fh:
    long_description = fh.read()

version = get_version('src/salespyforce/utils/version.py')

setuptools.setup(
    name='salespyforce',
    version=version,
    author='Jeff Shurtliff',
    author_email='jeff.shurtliff@rsa.com',
    description='A Python toolset for performing Salesforce API calls',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffshurtliff/salespyforce",
    project_urls={
        'Issue Tracker': 'https://github.com/jeffshurtliff/salespyforce/issues',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.6',
    install_requires=[
        "urllib3>=1.26.15",
        "requests>=2.27.1",
        "setuptools>=59.6.0",
        "PyYAML~=6.0"
    ],
    extras_require={
        'sphinx': [
            'Sphinx>=3.4.0',
            'sphinxcontrib-applehelp>=1.0.2',
            'sphinxcontrib-devhelp>=1.0.2',
            'sphinxcontrib-htmlhelp>=1.0.3',
            'sphinxcontrib-jsmath>=1.0.1',
            'sphinxcontrib-qthelp>=1.0.3',
            'sphinxcontrib-serializinghtml>=1.1.4'
        ],
    }
)
