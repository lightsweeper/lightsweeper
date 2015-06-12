#!/usr/bin/env python

import sys

from setuptools import setup

if sys.hexversion < 0x030200a1:
    print ("LightSweeper requires python 3.2 or higher.")
    print("Exiting...")
    sys.exit(1)

setup(name='LightSweeperAPI',
    version='0.6b',
    description='The LightSweeper API',
    author='The LightSweeper Team',
    author_email='codewizards@lightsweeper.org',
    url='http://www.lightsweeper.org',
    packages=['lsapi'],
    )
