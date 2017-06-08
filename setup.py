#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(
    name='SMPNetwork',
    version='0.0.2c',
    description='Simple Messaging Protocol between a server and multiple clients. '
                'Supports continuous connections and SSL.',
    author='Halil Ozercan',
    author_email='halilozercan@gmail',
    url='https://github.com/halilozercan/smp',
    requires=['schedule'],
    packages=find_packages(),
)
