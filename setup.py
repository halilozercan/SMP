#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(
    name='SMPNetwork',
    version='0.0.6',
    description='Simple Messaging Protocol between a server and multiple clients. '
                'Supports continuous connections and SSL.',
    author='Halil Ozercan',
    author_email='halilozercan@gmail',
    url='https://github.com/halilozercan/smp',
    packages=find_packages(),
)
