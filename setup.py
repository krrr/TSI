#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(name='tsi',
      packages=find_packages(),
      entry_points={'console_scripts': ['tsi = tsi:main_entry']})