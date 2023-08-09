#!/usr/bin/env python

from setuptools import setup, find_packages


# This setup is suitable for "python setup.py develop".

setup(name='openimage',
      version='0.0.1',
      description='Some helper functions to open SPM data from different controllers',
      author='Koen Lauwaet',
      author_email='koen.lauwaet@imdea.org',
      url='https://github.com/KoenImdea/',
      packages=find_packages(),
      install_requires=["numpy", "access2thematrix", "spiepy", "nanonispy"],
)
