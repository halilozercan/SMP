#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(
    name='SMPNetwork',
    version='0.0.1a',
    description='Simple Messaging Protocol between a server and multiple clients. It supports continuous connections.',
    author='Halil Ozercan',
    author_email='halilozercan@gmail',
    url='https://github.com/halilozercan/smp',
    download_url='https://github.com/halilozercan/smp/tarball/0.0.1a',
    packages=find_packages(),
)
