#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os
import logging
import shutil
import codecs
import re
import distutils

logging.basicConfig(level=logging.INFO)

if distutils.spawn.find_executable("npm") is None:
    if distutils.spawn.find_executable("node") is None:

        raise EnvironmentError(
            "Nodejs and npm are not installed, or the directory has not "
            "been added to the current PATH variable.")
    else:
        raise EnvironmentError(
            "Nodejs is accessible, but the npm executable isn't accessible."
            "Check your PATH variable."
        )

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
    
def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Akshay Aithal",
    author_email='akshay.aithal@gknautomotive.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description="Provide view for task results via a distributable link",
    entry_points={
        'console_scripts': [
            'result_linker=result_linker.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='result_linker',
    name='result_linker',
    packages=find_packages(include=['result_linker']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/audreyr/result_linker',
    version='0.1.0',
    zip_safe=False,
)
